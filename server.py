"""FastAPI layer over the interview graph.

Run:  python -m uvicorn server:app --reload
Then open http://127.0.0.1:8000
"""

import base64
import json
import os
import threading
import uuid
import webbrowser
from contextlib import asynccontextmanager
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from langgraph.types import Command
from pydantic import BaseModel

import agents
import documents
from graph import build_graph


@asynccontextmanager
async def lifespan(app: FastAPI):
    # The launchers set OPEN_BROWSER=1 so the page opens only once the server is ready.
    if os.getenv("OPEN_BROWSER") == "1":
        threading.Timer(1.0, webbrowser.open, ["http://127.0.0.1:8000"]).start()
    yield


app = FastAPI(title="Expert Interviewer", lifespan=lifespan)
graph = build_graph()

# Transcript store (mocked): a JSON snapshot per session, rewritten after every exchange.
SESSIONS_DIR = Path(__file__).parent / "sessions"
SESSIONS_DIR.mkdir(exist_ok=True)

MAX_UPLOAD_BYTES = 25_000_000  # all documents together
PREVIEW_CHARS = 600            # opening text shown for a flagged document


class Upload(BaseModel):
    name: str
    data_base64: str


class CreateSession(BaseModel):
    expert_name: str
    expert_role: str = ""
    case_background: str = ""
    documents: list[Upload] = []


class Message(BaseModel):
    message: str


class Review(BaseModel):
    keep: dict[str, bool]  # document id -> keep it?


def _config(session_id: str) -> dict:
    return {"configurable": {"thread_id": session_id}}


def _snapshot(session_id: str):
    snap = graph.get_state(_config(session_id))
    if not snap.values:
        raise HTTPException(404, "Session not found")
    return snap


def _state(session_id: str) -> dict:
    return _snapshot(session_id).values


def _phase(session_id: str) -> str:
    snap = _snapshot(session_id)
    if "review_documents" in snap.next:
        return "reviewing_documents"
    return snap.values.get("status", "")


def _public_doc(d: dict) -> dict:
    """A document as the page shows it: no full text, just its check and an opening preview."""
    out = {k: v for k, v in d.items() if k != "text"}
    out["chars"] = len(d.get("text", ""))
    if not d.get("check", {}).get("relevant", True):
        out["preview"] = d["text"][:PREVIEW_CHARS]
    return out


HIDDEN_UNTIL_GRADED = ("persona_name", "persona_profile", "rubric")


def _public(state: dict) -> dict:
    """What the interviewer may see: persona and look-fors stay hidden until grading."""
    out = {k: v for k, v in state.items() if k != "document_context"}
    out["documents"] = [_public_doc(d) for d in state.get("documents", [])]
    if not state.get("final_assessment"):
        out = {k: v for k, v in out.items() if k not in HIDDEN_UNTIL_GRADED}
    return out


def _view(session_id: str) -> dict:
    """The response the page needs after setup or document review."""
    state = _state(session_id)
    return {
        "session_id": session_id,
        "phase": _phase(session_id),
        "documents": [_public_doc(d) for d in state.get("documents", [])],
        "rubric": agents.load_rubric(),  # the fixed criteria; case-specific look-fors stay hidden
        "transcript": state.get("transcript", []),
    }


def _persist(state: dict) -> None:
    path = SESSIONS_DIR / f"{state['session_id']}.json"
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _require_phase(session_id: str, phase: str, message: str) -> None:
    if _phase(session_id) != phase:
        raise HTTPException(400, message)


@app.get("/")
def index():
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/config")
def config():
    return {"model": agents.MODEL, "mock_mode": agents.mock_mode(),
            "file_types": sorted(documents.SUPPORTED)}


@app.post("/session/create")
def create_session(body: CreateSession):
    raw = [base64.b64decode(u.data_base64) for u in body.documents]
    if sum(len(r) for r in raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(400, "The documents are over 25 MB in total.")
    docs = []
    for i, (u, data) in enumerate(zip(body.documents, raw), 1):
        kind, text = documents.extract_text(u.name, data)
        docs.append({"id": f"d{i}", "name": u.name, "kind": kind, "text": text})

    session_id = uuid.uuid4().hex[:12]
    # Checks the documents, then either pauses for document review (if any were
    # flagged) or starts the interview and pauses for the first question.
    # A random persona is assigned inside the graph and not returned here.
    graph.invoke({
        "session_id": session_id,
        "expert_name": body.expert_name,
        "expert_role": body.expert_role,
        "user_outline": body.case_background,
        "documents": docs,
        "transcript": [],
    }, _config(session_id))
    _persist(_state(session_id))
    return _view(session_id)


@app.post("/session/{session_id}/documents")
def review_documents(session_id: str, body: Review):
    _require_phase(session_id, "reviewing_documents", "There are no documents waiting for review.")
    graph.invoke(Command(resume=body.keep), _config(session_id))
    _persist(_state(session_id))
    return _view(session_id)


@app.post("/session/{session_id}/message")
def send_message(session_id: str, body: Message):
    _require_phase(session_id, "interviewing", "The interview isn't in progress.")
    graph.invoke(Command(resume={"type": "message", "message": body.message}), _config(session_id))
    state = _state(session_id)
    _persist(state)
    return {"reply": state["transcript"][-1], "transcript": state["transcript"]}


@app.post("/session/{session_id}/end")
def end_interview(session_id: str):
    _require_phase(session_id, "interviewing", "The interview isn't in progress.")
    graph.invoke(Command(resume={"type": "end"}), _config(session_id))
    state = _state(session_id)
    _persist(state)
    return state["final_assessment"]


@app.get("/session/{session_id}")
def get_session(session_id: str):
    return _public(_state(session_id)) | {"phase": _phase(session_id)}


@app.get("/session/{session_id}/results")
def get_results(session_id: str):
    state = _state(session_id)
    if "final_assessment" not in state:
        raise HTTPException(400, "Interview not graded yet")
    return state["final_assessment"]
