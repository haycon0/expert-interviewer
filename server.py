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

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from langgraph.types import Command
from starlette.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel

import access
import agents
import documents
import media
import model_catalog
from graph import build_graph


@asynccontextmanager
async def lifespan(app: FastAPI):
    # The launchers set OPEN_BROWSER=1 so the page opens only once the server is ready.
    if os.getenv("OPEN_BROWSER") == "1":
        threading.Timer(1.0, webbrowser.open, ["http://127.0.0.1:8000"]).start()
    yield


app = FastAPI(title="Expert Interviewer", lifespan=lifespan)
# Password login and the online safety switch (see access.py). Added before the host
# check, so the host check runs first.
app.middleware("http")(access.middleware)
# Answer only to known addresses: this computer, plus the public address when hosted
# (RENDER_EXTERNAL_HOSTNAME or ALLOWED_HOSTS). Blocks "DNS rebinding", where a website
# points its domain at 127.0.0.1 to reach the app. ("testserver" is FastAPI's test client.)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=access.allowed_hosts())
graph = build_graph()


@app.get("/healthz")
def healthz():
    """For the hosting service's health check. Needs no login and reveals nothing."""
    return {"ok": True}
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")


def _sessions_dir() -> Path | None:
    """Where session snapshots are saved: outside the project folder, so cloud-synced
    folders (OneDrive, iCloud) don't upload case documents. None if saving is off."""
    if os.getenv("SAVE_SESSIONS", "1").strip() == "0":
        return None
    if custom := os.getenv("SESSIONS_DIR", "").strip():
        return Path(custom)
    if os.name == "nt" and os.getenv("LOCALAPPDATA"):
        base = Path(os.environ["LOCALAPPDATA"]) / "ExpertInterviewer"
    elif (Path.home() / "Library" / "Application Support").exists():
        base = Path.home() / "Library" / "Application Support" / "ExpertInterviewer"
    else:
        base = Path.home() / ".expert-interviewer"
    return base / "sessions"


# Transcript store (mocked): a JSON snapshot per session, rewritten after every exchange.
SESSIONS_DIR = _sessions_dir()
if SESSIONS_DIR:
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

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
    models: dict[str, str] = {}  # agent -> "provider:model-name"; missing agents use the .env defaults
    media: dict[str, str] = {}   # {"mode": "text"|"voice"|"face", "voice", "voice_id", "face"}


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


def _reveal_persona() -> bool:
    """REVEAL_PERSONA=1 in .env shows the persona during the interview, for testing.
    Leave it out (the default) to keep the persona hidden until grading."""
    model_catalog.reload_env()
    return os.getenv("REVEAL_PERSONA", "").strip() == "1"


def _public(state: dict) -> dict:
    """What the interviewer may see: persona and look-fors stay hidden until grading."""
    out = {k: v for k, v in state.items() if k != "document_context"}
    out["documents"] = [_public_doc(d) for d in state.get("documents", [])]
    out["persona_revealed"] = state.get("persona_profile") if _reveal_persona() else None
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
        "models": state.get("models", {}),
        "media": state.get("media", {"mode": "text"}),
        # Only when REVEAL_PERSONA=1 (testing); otherwise the persona stays secret until grading.
        "persona": state.get("persona_profile") if _reveal_persona() else None,
    }


def _persist(state: dict) -> None:
    if not SESSIONS_DIR:
        return
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
    return {"file_types": sorted(documents.SUPPORTED), "password_protected": bool(access.password())}


@app.get("/models")
def models():
    """The model catalog with each model's setup status (re-reads .env every time)."""
    return model_catalog.catalog_with_status()


@app.get("/models/status")
def models_status(id: str):
    """Setup status of any model ID, including ones typed in that aren't in the catalog."""
    model_catalog.reload_env()
    return model_catalog.model_status(id.strip(), model_catalog.load_catalog())


def _resolve_models(chosen: dict[str, str]) -> dict[str, str]:
    """Fill in missing agents from .env and refuse any model that isn't set up."""
    model_catalog.reload_env()
    defaults = model_catalog.default_models()
    models = {a: (chosen.get(a) or defaults[a]).strip() for a in model_catalog.AGENTS}
    if model_catalog.forced_demo():
        return {a: model_catalog.DEMO for a in models}
    catalog = model_catalog.load_catalog()
    edition = catalog.get("edition") or {}
    if not edition.get("allow_custom_models", True):
        offered = {m["id"] for m in catalog["models"]}
        if extra := sorted(set(models.values()) - offered):
            raise HTTPException(400, f"{', '.join(extra)} isn't offered in this version of the app. "
                                     "To use other models, set it up on your own computer (see SETUP.md on GitHub).")
    problems = [model_catalog.describe_problems(m, st, catalog)
                for m in sorted(set(models.values()))
                if not (st := model_catalog.model_status(m, catalog))["ready"]]
    if problems:
        raise HTTPException(400, " ".join(problems))
    return models


@app.post("/session/create")
def create_session(body: CreateSession):
    raw = [base64.b64decode(u.data_base64) for u in body.documents]
    if sum(len(r) for r in raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(400, "The documents are over 25 MB in total.")
    docs = []
    for i, (u, data) in enumerate(zip(body.documents, raw), 1):
        kind, text = documents.extract_text(u.name, data)
        docs.append({"id": f"d{i}", "name": u.name, "kind": kind, "text": text})
    models = _resolve_models(body.models)
    media_choice = _resolve_media(body.media)
    if limit := access.take_interview():
        raise HTTPException(429, limit)

    session_id = uuid.uuid4().hex[:12]
    # Checks the documents, then either pauses for document review (if any were
    # flagged) or starts the interview and pauses for the first question.
    # A random persona is assigned inside the graph and not returned here.
    graph.invoke({
        "session_id": session_id,
        "expert_name": body.expert_name,
        "expert_role": body.expert_role,
        "user_outline": body.case_background,
        "models": models,
        "media": media_choice,
        "documents": docs,
        "transcript": [],
    }, _config(session_id))
    _persist(_state(session_id))
    return _view(session_id)


@app.post("/session/{session_id}/documents")
def review_documents(session_id: str, body: Review):
    _require_phase(session_id, "reviewing_documents", "There are no documents waiting for review.")
    # Wrapped so an empty choice ("remove all") still counts as an answer.
    graph.invoke(Command(resume={"keep": body.keep}), _config(session_id))
    _persist(_state(session_id))
    return _view(session_id)


@app.post("/session/{session_id}/message")
def send_message(session_id: str, body: Message):
    _require_phase(session_id, "interviewing", "The interview isn't in progress.")
    asked = sum(1 for t in _state(session_id)["transcript"] if t["speaker"] == "user")
    if limit := access.question_limit_error(asked):
        raise HTTPException(429, limit)
    graph.invoke(Command(resume={"type": "message", "message": body.message[:4000]}), _config(session_id))
    state = _state(session_id)
    _persist(state)
    return {"reply": state["transcript"][-1], "transcript": state["transcript"]}


@app.post("/session/{session_id}/end")
def end_interview(session_id: str):
    phase = _phase(session_id)
    if phase not in ("interviewing", "grading"):
        raise HTTPException(400, "The interview isn't in progress.")
    try:
        # "grading" means an earlier grading attempt failed: pick up where it stopped.
        graph.invoke(Command(resume={"type": "end"}) if phase == "interviewing" else None,
                     _config(session_id))
    except Exception as e:
        grader = _state(session_id).get("models", {}).get("grader", "the grader model")
        raise HTTPException(502, f"Grading didn't finish ({type(e).__name__}). Click End & grade to try "
                                 f"again. If it keeps failing, {grader} may be too small for grading; "
                                 "start a new interview with a stronger grader.")
    state = _state(session_id)
    _persist(state)
    return state["final_assessment"]


# ---------------------------------------------------------------------------
# Voice and face (see media.py and docs/VOICE-AND-FACE.md)
# ---------------------------------------------------------------------------

def _resolve_media(choice: dict[str, str]) -> dict:
    """Validate the conversation mode and its voice/face services."""
    mode = choice.get("mode", "text")
    if mode not in ("text", "voice", "face"):
        raise HTTPException(400, f"Unknown conversation mode '{mode}'.")
    if mode == "text":
        return {"mode": "text"}
    model_catalog.reload_env()
    catalog = media.load()
    out = {"mode": mode, "voice": choice.get("voice", "browser"), "voice_id": choice.get("voice_id", "")}
    needed = [("voice", out["voice"])]
    if mode == "face":
        out["face"] = choice.get("face", "builtin")
        needed.append(("face", out["face"]))
        if catalog["face"].get(out["face"], {}).get("needs_voice_audio") and out["voice"] == "browser":
            raise HTTPException(400, f"{catalog['face'][out['face']]['name']} needs OpenAI, ElevenLabs, "
                                     "or Deepgram as the voice service, not the browser's built-in voice.")
    for kind, pid in needed:
        st = media.status(kind, pid, catalog)
        if any(p["type"] == "unknown" for p in st["problems"]):
            raise HTTPException(400, f"The {kind} option '{pid}' isn't offered in this version of the app. "
                                     "To use it, set the app up on your own computer (see SETUP.md on GitHub).")
        if not st["ready"]:
            missing = ", ".join(p.get("key_env") or p.get("name") or p["type"] for p in st["problems"])
            raise HTTPException(400, f"{catalog[kind].get(pid, {}).get('name', pid)} isn't set up "
                                     f"(missing: {missing}). See docs/VOICE-AND-FACE.md.")
    return out


def _media_call(fn, *args):
    try:
        return fn(*args)
    except media.MediaError as e:
        raise HTTPException(502, str(e))
    except KeyError as e:
        raise HTTPException(502, f"Unexpected response from the service (missing {e}).")


@app.get("/media")
def media_options():
    """Voice and face options with each one's setup status (re-reads .env)."""
    return media.catalog_with_status()


@app.get("/media/voices")
def media_voices(provider: str):
    return _media_call(media.voices, provider)


@app.post("/speech/transcribe")
async def speech_transcribe(request: Request, provider: str):
    audio = await request.body()
    if len(audio) > MAX_UPLOAD_BYTES:
        raise HTTPException(400, "That recording is too long.")
    return {"text": _media_call(media.transcribe, provider, audio, request.headers.get("content-type", ""))}


class Speak(BaseModel):
    provider: str
    text: str
    voice: str = ""
    format: str = "mp3"  # or "pcm16" for lip-sync avatars


@app.post("/speech/synthesize")
def speech_synthesize(body: Speak):
    audio, mime = _media_call(media.synthesize, body.provider, body.text[:5000], body.voice, body.format)
    return Response(content=audio, media_type=mime)


@app.post("/avatar/{provider}/start")
def avatar_start(provider: str):
    return _media_call(media.avatar_start, provider)


@app.post("/avatar/did/{action}")
def avatar_did(action: str, payload: dict):
    return _media_call(media.did_call, action, payload.get("id", ""), payload)


@app.post("/avatar/{provider}/stop")
def avatar_stop(provider: str, payload: dict):
    media.avatar_stop(provider, payload)
    return {"ok": True}


@app.get("/session/{session_id}")
def get_session(session_id: str):
    return _public(_state(session_id)) | {"phase": _phase(session_id)}


@app.get("/session/{session_id}/results")
def get_results(session_id: str):
    state = _state(session_id)
    if "final_assessment" not in state:
        raise HTTPException(400, "Interview not graded yet")
    return state["final_assessment"]
