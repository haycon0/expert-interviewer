"""LangGraph orchestration for the Expert Interviewer (the "Master Agent").

START -> initialize_session -> run_research -> start_interview
      -> check_interview_end <-> expert_response   (interview loop, pauses for user input)
      -> generate_rubric -> grade_interview -> finalize_session -> END

The rubric isn't needed until grading, so run_research kicks off the Criteria
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

PERSONAS_FILE = Path(__file__).parent / "personas.json"


def load_personas() -> list[dict]:
    """Personas are config-driven: edit personas.json to add more."""
    return json.loads(PERSONAS_FILE.read_text(encoding="utf-8"))


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class InterviewState(TypedDict, total=False):
    session_id: str
    expert_name: str
    persona_name: str
    persona_profile: dict
    expert_role: str
    user_outline: str  # case background: the complaint or suspected misconduct
    case_file: str  # optional uploaded evidence; cleared after research

    research_package: dict
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

def initialize_session(state: InterviewState) -> dict:
    # Persona is drawn at random and kept hidden from the interviewer until grading.
    persona = random.choice(load_personas())
    return {
        "persona_name": persona["name"],
        "persona_profile": persona,
        "interview_started": False,
        "interview_complete": False,
        "status": "researching",
        "created_at": now(),
    }


_executor = ThreadPoolExecutor(max_workers=4)
_rubric_jobs: dict[str, Future] = {}


def _build_rubric(state: InterviewState, research_package: dict) -> dict:
    return agents.create_rubric(research_package)


def run_research(state: InterviewState) -> dict:
    pkg = agents.research_expert(
        state["expert_name"], state.get("expert_role", ""),
        state.get("user_outline", ""), state.get("case_file", ""),
    )
    _rubric_jobs[state["session_id"]] = _executor.submit(_build_rubric, state, pkg)
    # Drop the raw case file so it isn't re-saved with every checkpoint.
    return {"research_package": pkg, "case_file": "", "status": "starting_interview"}


def generate_rubric(state: InterviewState) -> dict:
    job = _rubric_jobs.pop(state["session_id"], None)
    try:
        rubric = job.result()  # waits only if the interview was shorter than rubric generation
    except Exception:  # no job (e.g. server restarted) or it failed: build it now
        rubric = _build_rubric(state, state["research_package"])
    return {"rubric": rubric}


def start_interview(state: InterviewState) -> dict:
    greeting = agents.expert_reply(
        state["research_package"], state["persona_profile"], state.get("user_outline", ""), []
    )
    return {
        "interview_started": True,
        "status": "interviewing",
        "transcript": [{"speaker": "expert", "timestamp": now(), "message": greeting}],
    }


def check_interview_end(state: InterviewState) -> dict:
    # Pause the graph until the API resumes it with the user's next action.
    action = interrupt({"awaiting": "user_message"})
    if action.get("type") == "end":
        return {"interview_complete": True, "status": "grading"}
    return {"transcript": [{"speaker": "user", "timestamp": now(), "message": action["message"]}]}


def expert_response(state: InterviewState) -> dict:
    reply = agents.expert_reply(
        state["research_package"], state["persona_profile"],
        state.get("user_outline", ""), state["transcript"],
    )
    return {"transcript": [{"speaker": "expert", "timestamp": now(), "message": reply}]}


def grade_interview(state: InterviewState) -> dict:
    assessment = agents.grade_interview(
        state["rubric"], state["transcript"], state["research_package"],
        state.get("user_outline", ""), state["persona_profile"],
    )
    return {"final_assessment": assessment}


def finalize_session(state: InterviewState) -> dict:
    return {"status": "complete", "completed_at": now()}


def route_after_check(state: InterviewState) -> str:
    return "generate_rubric" if state.get("interview_complete") else "expert_response"


# --------------------------------------------------------------------------
# Graph
# --------------------------------------------------------------------------

def build_graph():
    g = StateGraph(InterviewState)
    for fn in [initialize_session, run_research, generate_rubric, start_interview,
               check_interview_end, expert_response, grade_interview, finalize_session]:
        g.add_node(fn.__name__, fn)

    g.add_edge(START, "initialize_session")
    g.add_edge("initialize_session", "run_research")
    g.add_edge("run_research", "start_interview")
    g.add_edge("start_interview", "check_interview_end")
    g.add_conditional_edges("check_interview_end", route_after_check,
                            ["expert_response", "generate_rubric"])
    g.add_edge("expert_response", "check_interview_end")
    g.add_edge("generate_rubric", "grade_interview")
    g.add_edge("grade_interview", "finalize_session")
    g.add_edge("finalize_session", END)

    # MemorySaver = mocked storage for the MVP; swap for PostgresSaver later.
    return g.compile(checkpointer=MemorySaver())
