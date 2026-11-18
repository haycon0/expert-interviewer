"""Grade a complete (or nearly complete) script with rubric v2.2.

usage: python debug/tools/grade_script.py <script-id> <run-label> [model] [--strong-closing] [--runs N]
--runs N averages N independent gradings, as GRADER_RUNS=N does in the app.
Saves the full report (with the raw grader output) to debug/gradings/<script-id>_<run-label>.json.
"""
import json
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

load_dotenv(Path.cwd() / ".env")
import agents
import documents
import grading_v2
import graph

sid, label = sys.argv[1], sys.argv[2]
model = next((a for a in sys.argv[3:] if ":" in a), "anthropic:claude-haiku-5-5")
runs = int(sys.argv[sys.argv.index("--runs") + 1]) if "--runs" in sys.argv else 1
script = json.loads(Path(f"debug/scripts/{sid}.json").read_text(encoding="utf-8"))
transcript = list(script["transcript"])
if "--strong-closing" in sys.argv:  # the strong script leaves its closing question for the user
    q = script["resume_hint"].split(': "', 1)[1].split('" If his answer', 1)[0]
    transcript += [{"speaker": "user", "message": q}, {"speaker": "expert", "message": "No, I don't have anything to add."}]
background = Path(script["case_background_file"]).read_text(encoding="utf-8")
docs = []
for i, rel in enumerate(script["documents"], 1):  # every document is kept, as if the user kept it at the check
    f = Path(rel)
    docs.append({"id": f"d{i}", "name": f.name, "text": documents.extract_text(f.name, f.read_bytes())[1]})
context, _ = documents.build_context(docs, script["expert_name"])
personas = json.loads(Path("personas.json").read_text(encoding="utf-8"))
persona = dict(next(p for p in personas if p["name"] == script["persona"]))
persona["active_variables"] = (graph.chosen_variables(persona, graph.load_variables(), script.get("picks", []), False)
                               if script.get("variables") == "choose" else [])
rubric = grading_v2.load_rubric()
turns = grading_v2.number_turns(transcript)
t0 = time.time()
prompt = grading_v2._prompt(rubric, turns, script["expert_name"], background, context, persona, True)
raws = grading_v2.grade_many(prompt, model, rubric, True, runs)
raw = grading_v2.combine(rubric, raws)
report = grading_v2.score(rubric, turns, raw)
if runs > 1:
    report["grader_runs"] = [grading_v2.score(rubric, turns, r)["overall_score"] for r in raws]
report.pop("turns")
out = {"script": sid, "run": label, "model": model, "graded": time.strftime("%Y-%m-%d %H:%M"),
       "seconds": round(time.time() - t0), "questions": sum(1 for x in transcript if x["speaker"] == "user"),
       "closing_added": "--strong-closing" in sys.argv and transcript[-2:], "runs": runs, "report": report, "grader_output": raws if runs > 1 else raw}
Path("debug/gradings").mkdir(exist_ok=True)
Path(f"debug/gradings/{sid}_{label}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"{sid} {label}: {report['status']} {report['overall_score']} {report['band']} "
      f"areas={[a['total'] for a in report['areas']]} cap={(report['cap'] or {}).get('flag')}"
      + (f" runs={report['grader_runs']}" if runs > 1 else "")
      + f" unfollowed={len(report['unfollowed_leads'])}")
