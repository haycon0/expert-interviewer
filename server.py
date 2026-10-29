"""FastAPI layer over the interview graph.

Run:  python -m uvicorn server:app --reload
Then open http://127.0.0.1:8000
"""

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


class CreateSession(BaseModel):
    expert_name: str
    expert_role: str = ""
    case_background: str = ""
    case_file: str = ""  # text of an optional uploaded file (events log, notes, etc.)


class Message(BaseModel):
    message: str


def _config(session_id: str) -> dict:
    return {"configurable": {"thread_id": session_id}}


def _state(session_id: str) -> dict:
    snap = graph.get_state(_config(session_id))
    if not snap.values:
        raise HTTPException(404, "Session not found")
    return snap.values


HIDDEN_UNTIL_GRADED = ("persona_name", "persona_profile", "rubric")


def _public(state: dict) -> dict:
    """What the interviewer may see: persona and look-fors stay hidden until grading."""
    if state.get("final_assessment"):
        return state
    return {k: v for k, v in state.items() if k not in HIDDEN_UNTIL_GRADED}


def _persist(state: dict) -> None:
    path = SESSIONS_DIR / f"{state['session_id']}.json"
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


@app.get("/")
def index():
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/config")
def config():
    return {"model": agents.MODEL, "mock_mode": agents.mock_mode()}


@app.post("/session/create")
def create_session(body: CreateSession):
    session_id = uuid.uuid4().hex[:12]
    # Runs research -> opening greeting, then pauses for the user's first question.
    # A random persona is assigned inside the graph and not returned here.
    graph.invoke({
        "session_id": session_id,
        "expert_name": body.expert_name,
        "expert_role": body.expert_role,
        "user_outline": body.case_background,
        "case_file": body.case_file,
        "transcript": [],
    }, _config(session_id))
    state = _state(session_id)
    _persist(state)
    return {
        "session_id": session_id,
        "research_package": state["research_package"],
        "rubric": agents.load_rubric(),  # the fixed criteria; expert-specific look-fors stay hidden
        "transcript": state["transcript"],
    }


@app.post("/session/{session_id}/message")
def send_message(session_id: str, body: Message):
    if _state(session_id).get("interview_complete"):
        raise HTTPException(400, "Interview already ended")
    graph.invoke(Command(resume={"type": "message", "message": body.message}), _config(session_id))
    state = _state(session_id)
    _persist(state)
    return {"reply": state["transcript"][-1], "transcript": state["transcript"]}


@app.post("/session/{session_id}/end")
def end_interview(session_id: str):
    if _state(session_id).get("interview_complete"):
        raise HTTPException(400, "Interview already ended")
    graph.invoke(Command(resume={"type": "end"}), _config(session_id))
    state = _state(session_id)
    _persist(state)
    return state["final_assessment"]


@app.get("/session/{session_id}")
def get_session(session_id: str):
    return _public(_state(session_id))


@app.get("/session/{session_id}/results")
def get_results(session_id: str):
    state = _state(session_id)
    if "final_assessment" not in state:
        raise HTTPException(400, "Interview not graded yet")
    return state["final_assessment"]
