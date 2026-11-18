"""Persona consistency test: are the personas noticeably different, and does each stay in character?

usage: python debug/tools/persona_test.py <run-label> [--witness provider:model] [--judge provider:model]

The same 12 questions (the Fastow/Enron case) are put live to the witness once per persona,
with no variations, so only the persona differs. A judge model then:
  1. rates each transcript for consistency: does every answer fit that persona? (0-4, with the turns that drift)
  2. reads the three transcripts unlabeled and in random order, and matches each to a persona description.

Passes when every persona is rated 3 or more for consistency and the judge matches all three.
Saves everything to debug/gradings/persona-consistency_<run-label>.json.
"""
import json
import os
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
load_dotenv(Path.cwd() / ".env")
import agents
import documents

label = sys.argv[1]
arg = lambda flag, default: sys.argv[sys.argv.index(flag) + 1] if flag in sys.argv else default
WITNESS = arg("--witness", os.getenv("MODEL_WITNESS") or os.getenv("MODEL") or "anthropic:claude-haiku-5-5")
JUDGE = arg("--judge", os.getenv("MODEL_GRADER") or "anthropic:claude-sonnet-5-5")
PASS_RATING = 3

CASE = json.loads(Path("debug/cases/enron-fastow.json").read_text(encoding="utf-8"))
QUESTIONS = [
    # The opening: who we represent, privilege, ground rules.
    "Good morning, Mr. Fastow. My name is Jordan Reyes. The Special Investigative Committee of Enron's Board has "
    "retained us to investigate the LJM and Chewco transactions. We represent the Committee and the company, not you; "
    "we aren't your lawyers and can't give you legal advice. This interview is privileged, but the privilege belongs to "
    "the company, which may decide to share what you tell us, including with the government. Do you understand?",
    "If you're guessing or estimating, please tell me, and if a question is unclear, ask me. Is that all right?",
    # Open questions: room to ramble, boast or say little.
    "Tell me about your role as CFO.",
    "Walk me through how LJM1 came about in 1999.",
    "What did you tell the Board on June 28, 1999 about how you would be compensated?",
    # A challenge: how does each take being doubted?
    "Are you sure about that? The Board materials don't say much about your compensation.",
    "How did Michael Kopper come to run Chewco?",
    "Who at Enron knew Kopper was involved in Chewco?",
    "How do you know that?",
    # A document that points at him.
    "I'd like to show you the Southampton Place partnership agreement, dated March 20, 2000. It lists a $25,000 "
    "contribution from the Fastow Family Foundation, which received about $4.5 million two months later. "
    "How does that fit with what you told the Board?",
    "Is there anything else you think the Committee should know?",
    "Please keep any related documents and keep today confidential. Thank you for your time.",
]


def case_context() -> tuple[str, str]:
    background = Path(CASE["case_background_file"]).read_text(encoding="utf-8") \
        if CASE.get("case_background_file") else CASE["case_background"]
    docs = []
    for i, rel in enumerate(CASE["documents"], 1):
        f = Path(rel)
        docs.append({"id": f"d{i}", "name": f.name, "text": documents.extract_text(f.name, f.read_bytes())[1]})
    return background, documents.build_context(docs, CASE["expert_name"])[0]


def interview(persona: dict, background: str, context: str) -> list[dict]:
    persona = {**persona, "active_variables": []}
    ask = lambda tr: agents.split_mood(agents.expert_reply(
        CASE["expert_name"], CASE["expert_role"], persona, background, context, tr, WITNESS))[0]
    transcript = [{"speaker": "expert", "message": ask([])}]
    for q in QUESTIONS:
        transcript.append({"speaker": "user", "message": q})
        transcript.append({"speaker": "expert", "message": ask(transcript)})
    return transcript


def text(transcript: list[dict]) -> str:
    return "\n\n".join(f"T{i} [{'INTERVIEWER' if t['speaker'] == 'user' else 'WITNESS'}] {t['message']}"
                       for i, t in enumerate(transcript, 1))


def describe(p: dict) -> str:
    return f"{p['name']} ({', '.join(p['traits'])}): {p['witness_posture']}"


class Consistency(BaseModel):
    off_character_turns: list[str] = Field(description="Witness turn IDs whose manner doesn't fit the persona, "
                                                       "each with a few words on why, e.g. 'T9: suddenly chatty'")
    rating: int = Field(description="0-4: 4 every answer fits; 3 nearly all fit, small slips; 2 several answers "
                                    "drift; 1 mostly out of character; 0 no recognizable persona")
    reason: str


class Match(BaseModel):
    transcript: str = Field(description="Transcript letter, e.g. A")
    persona: str = Field(description="Exact persona name")
    confidence: int = Field(description="0-100")
    reason: str


class Matching(BaseModel):
    matches: list[Match]
    how_different: str = Field(description="One or two sentences on how clearly the witnesses differ")


def judge_consistency(p: dict, transcript: list[dict]) -> dict:
    prompt = (
        "A witness in a practice legal interview was told to play this persona:\n"
        f"{describe(p)}\nIts possible shift during the interview: {p['variable']}\n\n"
        "Judge only the witness's manner (tone, length, cooperativeness, how it handles being doubted or shown a "
        "document), not whether its facts are right. A change the persona's own 'possible shift' allows is in "
        "character. List every witness turn that doesn't fit, then rate consistency 0-4.\n\n"
        f"Transcript:\n{text(transcript)}")
    return agents.structured("grader", Consistency, JUDGE).invoke(prompt).model_dump()


def judge_matching(personas: list[dict], transcripts: dict[str, list[dict]]) -> dict:
    prompt = (
        "Three practice legal interviews asked the same witness the same questions. Each time, the witness played "
        "a different one of these personas:\n"
        + "\n".join(f"- {describe(p)}" for p in personas)
        + "\n\nMatch each transcript to the persona it played (each persona exactly once), judging only manner.\n\n"
        + "\n\n".join(f"=== Transcript {k} ===\n{text(t)}" for k, t in transcripts.items()))
    return agents.structured("grader", Matching, JUDGE).invoke(prompt).model_dump()


def main():
    t0 = time.time()
    personas = json.loads(Path("personas.json").read_text(encoding="utf-8"))
    background, context = case_context()
    with ThreadPoolExecutor(len(personas)) as pool:
        transcripts = dict(zip([p["name"] for p in personas],
                               pool.map(lambda p: interview(p, background, context), personas)))
        consistency = dict(zip([p["name"] for p in personas],
                               pool.map(lambda p: judge_consistency(p, transcripts[p["name"]]), personas)))
    order = random.sample([p["name"] for p in personas], len(personas))
    letters = {chr(65 + i): name for i, name in enumerate(order)}
    matching = judge_matching(personas, {k: transcripts[v] for k, v in letters.items()})
    for m in matching["matches"]:
        m["actual"] = letters.get(m["transcript"].strip().upper()[:1], "?")
        m["correct"] = m["persona"].strip().startswith(m["actual"])  # the judge may add the traits
    matched = sum(m["correct"] for m in matching["matches"])
    consistent = all(c["rating"] >= PASS_RATING for c in consistency.values())
    result = {
        "run": label, "witness_model": WITNESS, "judge_model": JUDGE, "date": time.strftime("%Y-%m-%d %H:%M"),
        "seconds": round(time.time() - t0),
        "passed": consistent and matched == len(personas),
        "criteria": f"Every persona rated {PASS_RATING}+ of 4 for consistency, and all {len(personas)} matched.",
        "consistency": consistency, "matched": f"{matched} of {len(personas)}", "matching": matching,
        "transcripts": transcripts,
    }
    Path("debug/gradings").mkdir(exist_ok=True)
    out = Path(f"debug/gradings/persona-consistency_{label}.json")
    out.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"persona-consistency {label}: {'PASS' if result['passed'] else 'FAIL'} "
          f"consistency={ {k: v['rating'] for k, v in consistency.items()} } matched={result['matched']} "
          f"({result['seconds']}s) -> {out}")


if __name__ == "__main__":
    main()
