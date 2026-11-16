"""Build debug/scripts/fastow-poor-prioritization.json: the strong Fastow interview with a long,
well-run detour into low-value topics placed early, before the key issues, to show that rubric
v2.2 doesn't consider prioritization or use of time.

Run from the project folder: python debug/tools/build_time_script.py
Everything else matches debug/scripts/fastow-final-question.json plus its closing question.
The detour topics come from the same June 28, 1999 Board meeting (events log E0001, E0003,
E0013, E0020); details beyond the log are made up for the exercise.
"""
import json
from pathlib import Path

SRC = json.loads(Path("debug/scripts/fastow-final-question.json").read_text(encoding="utf-8"))
t = [dict(x) for x in SRC["transcript"]]
U = lambda m: {"speaker": "user", "message": m}
E = lambda m: {"speaker": "expert", "message": m}

DETOUR = [
    # Board agenda
    U("Before we go on, tell me everything you remember about the rest of the agenda at that June 28, 1999 Board meeting."),
    E("It was a full agenda. The two-for-one stock split, a Compensation Committee report on the stock plan, Project LJM, a power project in Gaza that Joe Sutton presented, and a lease for a new company aircraft, which I presented."),
    # Aircraft lease
    U("Let's take the aircraft first. Tell me everything you remember about the aircraft lease."),
    E("The company was adding a Falcon 900EX. Rather than buy it outright, we set up a lease: an Enron affiliate or a trust would own the plane, and Enron would sublease it."),
    U("Why a lease rather than a purchase?"),
    E("It kept the asset off our balance sheet and gave us better financing terms. That was standard for corporate aircraft."),
    U("Who provided the financing?"),
    E("The Bank of Tokyo-Mitsubishi. The term sheet was from May 1999, I believe."),
    U("How sure are you about the bank and the date?"),
    E("Fairly sure about the bank. The date I'd want to check against the term sheet."),
    U("Who negotiated the financing terms with the bank?"),
    E("Our corporate finance group. I signed off on the structure."),
    U("Who in the corporate finance group?"),
    E("I don't recall the individual names. It was routine work for that team."),
    U("Was the lease guaranteed by Enron?"),
    E("Yes, under the guarantee policy the Board had approved earlier that year, in February."),
    U("How do you know the guarantee fell under that policy: did you review it yourself, or did someone tell you?"),
    E("The legal group confirmed it, and it was in the draft resolution."),
    U("Who would use the aircraft?"),
    E("Senior executives for business travel. Mostly international trips."),
    U("What did the Board ask you about the lease?"),
    E("Very little. It was a routine item. They approved it."),
    U("Do you know roughly what the lease cost the company each year?"),
    E("I don't remember the figure. The lease documents would show it."),
    U("Where would those documents be kept?"),
    E("With corporate finance, and the legal group would have the signed lease."),
    # Stock split
    U("Turning to the stock split. Tell me what you remember about how the two-for-one split was approved."),
    E("Shareholders had approved an increase in authorized shares in May 1999, on the condition that the Board declared at least a two-for-one split within two years. Ken and Jeff presented the split at the June meeting."),
    U("What was your role in the split?"),
    E("Not much. My group checked the share reserves and the mechanics with the transfer agent."),
    U("Who was the transfer agent?"),
    E("First Chicago Trust, I believe."),
    U("How certain are you of that?"),
    E("Reasonably certain. It was in the resolution."),
    U("When did the split take effect?"),
    E("In August 1999."),
    U("Did the split raise any concerns at the Board?"),
    E("No. It was expected. The stock had done well."),
    # Gaza project
    U("Next, the Gaza power project. Tell me everything you remember about it."),
    E("Enron International proposed a combined-cycle power plant in Gaza, about 136 megawatts, with a 20-year franchise and power purchase agreement. Joe Sutton presented it."),
    U("What was Global Finance's role in the project?"),
    E("We looked at the financing structure: the equity split, the letter of credit, and the bridge financing."),
    U("How was the equity to be split?"),
    E("Roughly a third each among Enron, Palestinian investors, and the public."),
    U("What return did the project promise?"),
    E("Around 18 percent, I think. Joe would know the exact figure."),
    U("How do you know that figure: did you work on the model yourself?"),
    E("No, I saw it in the presentation. Joe's team built the model."),
    U("Who else at Enron worked on the Gaza financing?"),
    E("People on Joe's team at Enron International. I don't remember the names."),
    U("Did the Board approve the project?"),
    E("Yes, with an equity commitment of up to about $21 million."),
    # Global Finance staffing
    U("Going back to Global Finance for a moment. How many people worked in the group in 1999?"),
    E("A good number. It grew a lot that year. I'd guess well over a hundred by the end of it, but I'm estimating."),
    U("How did you recruit for the group?"),
    E("Mostly from investment banks and the big accounting firms, plus some internal transfers."),
    U("Where was the group located?"),
    E("In the Enron Building in Houston, on a couple of floors."),
    U("Who handled hiring decisions?"),
    E("Senior people in the group. I approved the senior hires myself."),
    U("Did the group have its own budget?"),
    E("Yes, it was part of the corporate budget, reviewed each year."),
]

i = next(k for k, x in enumerate(t) if x["speaker"] == "user" and x["message"].startswith("Next, I'd like to cover the Rhythms unwind"))
t[i:i] = DETOUR
closing = SRC["resume_hint"].split(': "', 1)[1].split('" If his answer', 1)[0]
t += [U(closing), E("No, I don't have anything to add.")]
for a, b in zip(t, t[1:]):
    assert a["speaker"] != b["speaker"]
detour_q = sum(1 for x in DETOUR if x["speaker"] == "user")
out = {**{k: v for k, v in SRC.items() if k != "transcript"},
       "name": "Fastow (Enron): strong, with poor prioritization",
       "description": (f"The strong Fastow interview, complete, with a {detour_q}-question detour into low-value topics "
                       "(the aircraft lease, the stock split, the Gaza power project, Global Finance staffing) placed "
                       "early, before the Rhythms unwind, Chewco, Southampton and the other key issues. Used to show that "
                       "rubric v2.2 doesn't consider prioritization or use of time. Click End & grade."),
       "resume_hint": "This interview is complete, including the close. Click End & grade.",
       "detour": {"questions": detour_q, "starts_at_turn": i + 1, "ends_at_turn": i + len(DETOUR)},
       "transcript": t}
Path("debug/scripts/fastow-poor-prioritization.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(len(t), "turns;", sum(1 for x in t if x["speaker"] == "user"), "questions; detour", detour_q, "questions at T", i + 1, "-", i + len(DETOUR))
