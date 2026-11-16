"""LangGraph orchestration for the Expert Interviewer (the "Master Agent").

START -> initialize_session -> verify_documents -> review_documents
      -> start_interview -> check_interview_end <-> expert_response   (interview loop)
      -> generate_rubric -> grade_interview -> finalize_session -> END

verify_documents checks every uploaded document for relevance. review_documents
pauses for the interviewer to keep or remove any flagged ones (it passes straight
through when nothing is flagged), then builds the document text the other agents use.

The rubric isn't needed until grading, so review_documents kicks off the Criteria
Agent in a background thread and the interview starts right away.
generate_rubric just collects that result (normally long finished) into state.
"""

import json
import operator
import random
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

import agents
import documents
import grading_v2

PERSONAS_FILE = Path(__file__).parent / "personas.json"


def load_personas() -> list[dict]:
    """Personas are config-driven: edit personas.json to add more."""
    return json.loads(PERSONAS_FILE.read_text(encoding="utf-8"))


VARIABLES_FILE = Path(__file__).parent / "variables.json"


def load_variables() -> dict:
    """Variable elements and how often they appear: edit variables.json to change them."""
    return json.loads(VARIABLES_FILE.read_text(encoding="utf-8"))


def draw_variables(persona: dict, config: dict, rng: random.Random = random) -> list[dict]:
    """Pick this interview's variable elements, following the rules in variables.json.

    Some interviews get none (1 - chance_of_any_variable). The rest get between 1 and
    max_variables elements, drawn from the persona's own variable (if it has one) plus
    up to max_general_variables of the general ones, each with one option chosen.
    """
    rules = config["rules"]
    if rng.random() >= rules["chance_of_any_variable"]:
        return []
    general = config["variables"]
    has_own = bool(persona.get("variable"))
    max_general = min(rules["max_general_variables"], len(general))
    most = min(rules["max_variables"], max_general + has_own)
    total = rng.randint(1, most)
    # The persona's own variable is needed when the general ones can't fill the count;
    # otherwise it's included about half the time.
    use_own = has_own and (total > max_general or rng.random() < 0.5)
    picked = []
    if use_own:
        picked.append({"name": "Persona variable", "description": persona["variable"]})
    for v in rng.sample(general, total - use_own):
        option = rng.choice(v["options"])
        picked.append({"name": v["name"], "value": option["label"], "description": option["guidance"]})
    return picked


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class InterviewState(TypedDict, total=False):
    session_id: str
    expert_name: str
    persona_name: str
    persona_profile: dict
    expert_role: str
    user_outline: str  # case background: the complaint or suspected misconduct
    media: dict  # {"mode": "text"|"voice"|"face", "voice": provider, "voice_id", "face": provider}
    debug: dict  # debugging mode only: {"persona", "variables", "picks", "twist", "skip_check", "script"}
    models: dict  # model per agent: {"witness", "checker", "criteria", "grader"} -> "provider:name"

    # Uploaded documents: {id, name, kind, text, check: {...}, keep, included_chars, trimmed}
    documents: list
    document_context: str  # kept documents combined, as the agents read them
    rubric: dict

    interview_started: bool
    interview_complete: bool

    # Append-only: nodes return new entries and the reducer concatenates them.
    transcript: Annotated[list, operator.add]

    final_assessment: dict
    status: str
    created_at: str
    completed_at: str


# --------------------------------------------------------------------------
# Nodes
# --------------------------------------------------------------------------

def chosen_variables(persona: dict, config: dict, picks: list[dict], twist: bool) -> list[dict]:
    """Variable elements chosen by hand in debugging mode: picks are [{name, value}]."""
    out = []
    if twist and persona.get("variable"):
        out.append({"name": "Persona variable", "description": persona["variable"]})
    by_name = {v["name"]: v for v in config["variables"]}
    for pick in picks:
        var = by_name.get(pick.get("name"))
        option = next((o for o in (var or {}).get("options", []) if o["label"] == pick.get("value")), None)
        if option:
            out.append({"name": var["name"], "value": option["label"], "description": option["guidance"]})
    return out


def initialize_session(state: InterviewState) -> dict:
    # Persona and its variable elements are drawn at random and kept hidden from the
    # interviewer until grading (they travel inside persona_profile). In debugging mode
    # either can be chosen instead.
    dbg = state.get("debug") or {}
    personas = load_personas()
    persona = dict(next((p for p in personas if p["name"] == dbg.get("persona")), None)
                   or random.choice(personas))
    variables = dbg.get("variables", "random")
    if variables == "none":
        persona["active_variables"] = []
    elif variables == "choose":
        persona["active_variables"] = chosen_variables(persona, load_variables(),
                                                       dbg.get("picks", []), dbg.get("twist", False))
    else:
        persona["active_variables"] = draw_variables(persona, load_variables())
    return {
        "persona_name": persona["name"],
        "persona_profile": persona,
        "interview_started": False,
        "interview_complete": False,
        "status": "checking_documents",
        "created_at": now(),
    }


_executor = ThreadPoolExecutor(max_workers=8)
_rubric_jobs: dict[str, Future] = {}


def verify_documents(state: InterviewState) -> dict:
    docs = state.get("documents", [])
    if (state.get("debug") or {}).get("skip_check"):
        skipped = {"relevant": True, "category": "relevant",
                   "summary": "(Not checked: the document check was skipped for debugging.)",
                   "reason": "Skipped in debugging mode."}
        return {"documents": [{**d, "check": skipped} for d in docs]}
    checks = list(_executor.map(
        lambda d: agents.check_document(d, state["expert_name"], state.get("expert_role", ""),
                                        state.get("user_outline", ""), state["models"]["checker"]),
        docs,
    ))
    return {"documents": [{**d, "check": c} for d, c in zip(docs, checks)]}


def review_documents(state: InterviewState) -> dict:
    docs = state.get("documents", [])
    flagged = [d for d in docs if not d["check"]["relevant"]]
    decisions = {}
    if flagged:
        # Pause until the interviewer decides which flagged documents to keep.
        decisions = interrupt({"awaiting": "document_review",
                               "flagged": [d["id"] for d in flagged]}).get("keep", {})
    # Flagged documents are removed unless the interviewer chose to keep them.
    docs = [{**d, "keep": d["check"]["relevant"] or bool(decisions.get(d["id"]))} for d in docs]
    kept = [d for d in docs if d["keep"]]
    context, notes = documents.build_context(kept, state["expert_name"])
    by_id = {n["id"]: n for n in notes}
    docs = [{**d, **by_id.get(d["id"], {})} for d in docs]

    # Interviews are graded with rubric v2.2. Debugging mode can ask for the previous
    # rubric (rubric.json) instead, for comparison; only that one needs the Criteria
    # agent's look-fors, which it starts on now, in the background.
    if _uses_previous_rubric(state):
        _rubric_jobs[state["session_id"]] = _executor.submit(
            agents.create_rubric, state["expert_name"], state.get("user_outline", ""), context,
            state["models"]["criteria"])
    return {"documents": docs, "document_context": context, "status": "starting_interview"}


def _uses_previous_rubric(state: InterviewState) -> bool:
    return (state.get("debug") or {}).get("rubric") == "previous"


def generate_rubric(state: InterviewState) -> dict:
    if not _uses_previous_rubric(state):
        return {"rubric": grading_v2.load_rubric()}
    job = _rubric_jobs.pop(state["session_id"], None)
    try:
        rubric = job.result()  # waits only if the interview was shorter than rubric generation
    except Exception:  # no job (e.g. server restarted) or it failed: build it now
        rubric = agents.create_rubric(state["expert_name"], state.get("user_outline", ""),
                                      state.get("document_context", ""), state["models"]["criteria"])
    return {"rubric": rubric}


def _reply(state: InterviewState, transcript: list) -> dict:
    """The witness's next transcript entry, with its mood when a face is shown."""
    mode = state.get("media", {}).get("mode", "text")
    text = agents.expert_reply(
        state["expert_name"], state.get("expert_role", ""), state["persona_profile"],
        state.get("user_outline", ""), state.get("document_context", ""), transcript,
        state["models"]["witness"], mode,
    )
    text, mood = agents.split_mood(text)
    entry = {"speaker": "expert", "timestamp": now(), "message": text}
    if mode == "face":
        entry["mood"] = mood or "neutral"
    return entry


def start_interview(state: InterviewState) -> dict:
    # A debugging script may have loaded a transcript already: pick up from there
    # instead of generating an opening line.
    opening = [] if state.get("transcript") else [_reply(state, [])]
    return {
        "interview_started": True,
        "status": "interviewing",
        "transcript": opening,
    }


def check_interview_end(state: InterviewState) -> dict:
    # Pause the graph until the API resumes it with the user's next action.
    action = interrupt({"awaiting": "user_message"})
    if action.get("type") == "end":
        return {"interview_complete": True, "status": "grading"}
    return {"transcript": [{"speaker": "user", "timestamp": now(), "message": action["message"]}]}


def expert_response(state: InterviewState) -> dict:
    return {"transcript": [_reply(state, state["transcript"])]}


def grade_interview(state: InterviewState) -> dict:
    if not _uses_previous_rubric(state):
        assessment = grading_v2.grade(
            state["rubric"], state["transcript"], state["expert_name"],
            state.get("user_outline", ""), state.get("document_context", ""),
            state["persona_profile"], state["models"]["grader"])
        return {"final_assessment": {**assessment, "models": state["models"]}}
    assessment = agents.grade_interview(
        state["rubric"], state["transcript"], state["expert_name"],
        state.get("user_outline", ""), state.get("document_context", ""), state["persona_profile"],
        state["models"]["grader"],
    )
    return {"final_assessment": {**assessment, "models": state["models"]}}


def finalize_session(state: InterviewState) -> dict:
    return {"status": "complete", "completed_at": now()}


def route_after_check(state: InterviewState) -> str:
    return "generate_rubric" if state.get("interview_complete") else "expert_response"


# --------------------------------------------------------------------------
# Graph
# --------------------------------------------------------------------------

def build_graph():
    g = StateGraph(InterviewState)
    for fn in [initialize_session, verify_documents, review_documents, generate_rubric,
               start_interview, check_interview_end, expert_response, grade_interview,
               finalize_session]:
        g.add_node(fn.__name__, fn)

    g.add_edge(START, "initialize_session")
    g.add_edge("initialize_session", "verify_documents")
    g.add_edge("verify_documents", "review_documents")
    g.add_edge("review_documents", "start_interview")
    g.add_edge("start_interview", "check_interview_end")
    g.add_conditional_edges("check_interview_end", route_after_check,
                            ["expert_response", "generate_rubric"])
    g.add_edge("expert_response", "check_interview_end")
    g.add_edge("generate_rubric", "grade_interview")
    g.add_edge("grade_interview", "finalize_session")
    g.add_edge("finalize_session", END)

    # MemorySaver = mocked storage for the MVP; swap for PostgresSaver later.
    return g.compile(checkpointer=MemorySaver())
