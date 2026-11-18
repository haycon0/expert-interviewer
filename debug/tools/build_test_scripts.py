"""Build the seven scenario test scripts in debug/scripts/ (all Fastow/Enron, all ready to grade).

Run from the project folder: python debug/tools/build_test_scripts.py

  fastow-easy-cooperative    a cooperative witness (same questions as the guarded one)
  fastow-hard-guarded        a guarded witness (same questions as the cooperative one)
  fastow-ends-early          the interviewer stops after the opening and background
  fastow-wrong-input         a stray payroll email among the case documents
  fastow-own-lawyer          the witness stops to get his own lawyer; handled correctly
  fastow-missed-llc-bonus    the strong interview, but an LLC paying LJM bonuses is never followed up
  fastow-walks-out           the witness walks out when confronted about Southampton

Most are cut from debug/scripts/fastow-final-question.json (the strong interview); the
cooperative and guarded ones are written here. Facts beyond the events log are made up.
"""
import json
from pathlib import Path

SCRIPTS = Path("debug/scripts")
STRONG = json.loads((SCRIPTS / "fastow-final-question.json").read_text(encoding="utf-8"))
MEDIOCRE = json.loads((SCRIPTS / "fastow-mediocre-complete.json").read_text(encoding="utf-8"))
T = [{"speaker": x["speaker"], "message": x["message"]} for x in STRONG["transcript"]]
CLOSING = STRONG["resume_hint"].split(': "', 1)[1].split('" If his answer', 1)[0]
U = lambda m: {"speaker": "user", "message": m}
E = lambda m: {"speaker": "expert", "message": m}
DONE = "This interview is finished. Click End & grade."
CASE = {k: STRONG[k] for k in ("expert_name", "expert_role", "case_background_file", "documents")}


def upto(n):
    """Turns 1..n of the strong interview (n is a turn number, 1-based)."""
    return [dict(x) for x in T[:n]]


def save(key, name, description, transcript, persona="The C-Suite", picks=None, resume_hint=DONE, **extra):
    for a, b in zip(transcript, transcript[1:]):
        assert a["speaker"] != b["speaker"], (key, a["message"][:60])
    out = {"name": name, "description": description, "persona": persona,
           "variables": "choose" if picks else "none", **({"picks": picks} if picks else {}),
           **CASE, **extra, "resume_hint": resume_hint, "transcript": transcript}
    (SCRIPTS / f"{key}.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{key}: {len(transcript)} turns, {sum(x['speaker'] == 'user' for x in transcript)} questions")


# ---------------------------------------------------------------------------
# Easy and hard: identical questions; only the witness's answers differ.
# Each row: (question, cooperative answer, guarded answer).
# ---------------------------------------------------------------------------
ROWS = [
    (T[1]["message"],
     "That's clear. You represent the Committee and the company, not me, and the company decides what to share. I'm happy to help however I can.",
     "Understood. You work for the company. I'll answer what I can."),
    (T[3]["message"], T[4]["message"],
     "You represent the company. The company controls the privilege. Can we move on?"),
    (T[5]["message"],
     "Of course. I'll be clear about what I remember and what I'm estimating.",
     "Fine."),
    ("Let's start with your role. As CFO, what were you responsible for?",
     "Financing the company: raising capital, managing the balance sheet, and our structured finance group, Global Finance. By 1999 that meant a lot of off-balance-sheet structures, which is how the partnerships came about.",
     "Financing the company."),
    ("What did that include day to day?",
     "Capital raising, the rating agencies, and the structured deals Global Finance did with outside investors.",
     "Raising capital. The balance sheet. Structured finance."),
    ("Who reported to you in Global Finance?",
     "Ben Glisan, who became Treasurer in 2000. Michael Kopper, who ran structured transactions. Jeff McMahon, who was Treasurer before Ben. And a large staff under them.",
     "A lot of people. Glisan. Kopper. Others."),
    ("Tell me everything you remember about how LJM1 came about in 1999.",
     "Enron had a big gain in Rhythms NetConnections stock that we couldn't sell, and Jeff Skilling wanted it protected. Nobody outside would hedge it, so we set up LJM1 with outside equity to do it. I raised the idea with Ken Lay and Jeff in mid-June 1999, and it went to the Board on June 28.",
     "Enron needed a hedge on its Rhythms position. LJM1 provided it."),
    ("What else do you remember about how it was set up?",
     "I put in a million dollars as general partner, and two outside limited partners put in more. Enron contributed restricted Enron stock, and LJM1 gave Enron a put on the Rhythms shares.",
     "I was the general partner. There were outside investors. Enron contributed stock."),
    ("Who first suggested that you serve as the general partner?",
     "I did. I raised it with Ken and Jeff as a way to get the deal done quickly.",
     "It was discussed with Ken and Jeff."),
    ("Who raised it with them first?",
     "That was me, as I said.",
     "I did."),
    ("At the June 28, 1999 Board meeting, what did you tell the Board about how you would be compensated?",
     "That I'd invest a million dollars as general partner and would not receive any current or future value of the Enron stock Enron contributed. The Board then waived the Code of Conduct so I could act as general partner.",
     "What was in the materials. That I wouldn't get value from the Enron stock."),
    ("How sure are you that's what you told them?",
     "Very sure. It's in the resolution and the minutes.",
     "It's in the minutes."),
    ("Next, the Rhythms unwind in early 2000. Who negotiated it for Enron?",
     "Rick Causey's group negotiated for Enron. Michael Kopper and I negotiated for LJM1.",
     "Causey's group."),
    ("And for LJM1?",
     "As I said, Michael and me.",
     "Kopper and I."),
    ("What do you remember about a partnership called Southampton Place?",
     "It bought part of a limited partner's interest in LJM1 in March 2000. My family foundation invested $25,000 in it, as did Michael, Ben Glisan and a few others.",
     "It was an investment vehicle."),
    ("Who invested in it?",
     "As I said: the Foundation, Michael through an entity of his, Ben Glisan, Kristina Mordaunt, and a couple of Global Finance employees.",
     "Various people. My family foundation was one."),
    ("What did the Foundation put in, and what did it receive?",
     "$25,000, and about $4.5 million back on May 1, 2000, after the Rhythms unwind.",
     "A small amount. It did well."),
    ("How much did it receive?",
     "About $4.5 million, as I said. The Foundation's statements would have the exact figure.",
     "I'd have to check. Several million."),
    ("Our information is roughly $4.5 million, about six weeks after it invested. Does that fit your memory?",
     "Yes, that's right.",
     "That sounds about right."),
    ("How does that fit with what you told the Board about not receiving value from the Enron stock?",
     "I understand why you ask. My view at the time was that the Foundation was separate from me, and that what I told the Board was about my economics as general partner. Looking back, I should have disclosed it.",
     "The Foundation isn't me. What I told the Board was about my economics as general partner."),
    ("Did you tell the Board, Mr. Lay, or Mr. Skilling about the Foundation's investment?",
     "No. I didn't think it was required. I can see now that it should have been.",
     "It didn't come up."),
    ("So that I have it right: none of them was told?",
     "Correct.",
     "Not by me."),
    ("Let's turn to Chewco. Why was Michael Kopper chosen to manage it rather than you?",
     "Our lawyers said that if a senior officer like me took part, it would have to be disclosed in the proxy statement. Michael wasn't a senior officer, so using him avoided that.",
     "Michael was suited to it."),
    ("What else went into that choice?",
     "Honestly, avoiding the proxy disclosure was one of the main reasons.",
     "There were disclosure considerations."),
    ("What were those disclosure considerations?",
     "The proxy disclosure, as I said.",
     "If a senior officer were involved, it would have to be in the proxy."),
    ("I'd like to show you the minutes of the November 5, 1997 Executive Committee meeting. Do you recognize them?",
     "Yes, those are the Committee's minutes from that call. The Corporate Secretary's office prepared them.",
     "They look like the Committee's minutes."),
    ("Do they mention Mr. Kopper's role in Chewco?",
     "No, they don't. I don't recall it being discussed on the call.",
     "No."),
    ("Turning to the LJM2 controls. How do you know Mr. Causey and Mr. Buy reviewed every LJM2 deal?",
     "I don't, really. That was the requirement, and I assumed it was followed. Some approval sheets were signed after the deals closed.",
     "That was the process."),
    ("Did you check that it was followed?",
     "No. I didn't check each one myself.",
     "Not personally."),
    ("Were any approval sheets signed after a deal closed?",
     "Yes, a few. Raptor I closed in April 2000, and its sheet was signed weeks later.",
     "It happened."),
    ("Which ones?",
     "Raptor I is the one I remember. The sheets would show the rest.",
     "Raptor I, maybe others. The sheets would show it."),
    ("Is there anything I haven't asked about that you think the Committee should know?",
     "Only that I relied on our accountants and lawyers throughout. I'll help however I can.",
     "No."),
    ("Who else should we speak with?",
     "Rick Causey and Rick Buy on the approvals, Ben Glisan on the Raptors, Michael Kopper on Chewco and Southampton, and Jeff McMahon on the negotiations.",
     "Causey. Buy. Kopper."),
    (CLOSING, "Understood. Nothing to add or correct. Thank you.", "Understood."),
]


def easy_hard(col, greeting):
    tr = [E(greeting)]
    for row in ROWS:
        tr += [U(row[0]), E(row[col])]
    return tr


SAME = (f"Same {len(ROWS)} questions as the {{other}} script, word for word; only the witness's answers differ. "
        "The guarded witness gives the same facts, but only when pressed with follow-up questions. "
        "Tests the rubric rule 'no automatic penalty for a difficult witness': the two should score about the same.")
save("fastow-easy-cooperative", "Fastow (Enron): test, easy (cooperative witness)",
     "A short, sound interview of a cooperative Fastow who volunteers facts and admits mistakes. " + SAME.format(other="guarded (hard)"),
     easy_hard(1, "Good morning. Andy Fastow. Happy to help however I can."),
     persona="The Average Witness",
     picks=[{"name": "Cooperativeness", "value": "Helpful"}, {"name": "Candor", "value": "Candid"},
            {"name": "Communication Style", "value": "Conversational"}])
save("fastow-hard-guarded", "Fastow (Enron): test, hard (guarded witness)",
     "The same interview as the cooperative (easy) script, with a guarded Fastow: short answers, nothing volunteered. " + SAME.format(other="cooperative (easy)"),
     easy_hard(2, "Andy Fastow. Let's get on with it."),
     persona="The Adverse Witness",
     picks=[{"name": "Cooperativeness", "value": "Guarded"}, {"name": "Candor", "value": "Selective"},
            {"name": "Communication Style", "value": "Terse"},
            {"name": "Degree of Self-interest", "value": "Concerned about Liability"}])

# ---------------------------------------------------------------------------
# Interview ends early: the opening, his role and the start of LJM1, then the
# interviewer stops (closing properly) before any key issue.
# ---------------------------------------------------------------------------
save("fastow-ends-early", "Fastow (Enron): test, interview ends early",
     "The strong interview's opening (full Upjohn warning, ground rules), his role, and the start of LJM1 "
     "(12 questions), then the interviewer has to stop for the day and closes properly. None of the key issues "
     "(the Board representation, Southampton, Chewco, the controls, the Raptors) is reached. Tests how a cut-off "
     "interview is graded: the rubric says it should be 'Not enough evidence', not a normal score.",
     upto(25) + [U("I'm sorry, Mr. Fastow, something urgent has come up and I'm going to have to stop here for today. "
                   "Please keep all related documents and notes, keep today confidential, and don't discuss it with "
                   "other witnesses. We'll be in touch to schedule time to continue."),
                 E("All right. Have someone call my office.")])

# ---------------------------------------------------------------------------
# Wrong input: the mediocre interview, with a stray payroll email added to the
# case documents and shown to the witness once.
# ---------------------------------------------------------------------------
med = [{"speaker": x["speaker"], "message": x["message"]} for x in MEDIOCRE["transcript"]]
i = next(k for k, x in enumerate(med) if x["speaker"] == "user" and x["message"].startswith("Is there anything I haven't asked"))
med[i:i] = [U("I'd like to show you an email from Enron Payroll Services dated November 2, 2001, about direct deposit changes. Do you recognize it?"),
            E("It looks like a payroll notice that went to every employee in Houston. I don't see what it has to do with LJM or anything we've discussed."),
            U("All right, let's set it aside.")
            , E("Fine.")]
save("fastow-wrong-input", "Fastow (Enron): test, wrong input (stray payroll email)",
     "The mediocre interview (79 questions) with a stray file in the case documents: a November 2001 payroll "
     "reminder sent to all Houston employees, which has nothing to do with the case. The interviewer even shows it "
     "to Fastow once. Tests the document check (it should flag the email before the interview starts) and, if you "
     "keep it, whether the grader still gives a normal score. Don't tick 'Skip the document check'.",
     med, documents=CASE["documents"] + ["debug/documents/Enron_Payroll_Email_Nov2001.txt"],
     resume_hint="The document check should flag the payroll email first. Keep or remove it, then click End & grade.")

# ---------------------------------------------------------------------------
# Witness wants his own lawyer: the strong interview up to the personal-interest
# questions, where he stops to get counsel. The interviewer handles it correctly.
# ---------------------------------------------------------------------------
save("fastow-own-lawyer", "Fastow (Enron): test, witness wants his own lawyer",
     "The strong interview through LJM1, Chewco, the LJM2 controls and the Raptor returns (59 questions). When asked "
     "about his personal interests, Fastow stops and insists on his own lawyer. The interviewer handles it correctly: "
     "gives no legal advice, stops, asks him to preserve documents and keep it confidential, and arranges to continue "
     "through his counsel. Tests that stopping for the witness's lawyer isn't penalized and that the unreached topics "
     "(Southampton, 2001) are treated fairly.",
     upto(119) + [
         U(T[119]["message"]),
         E("Before you go there, I'm going to stop. I'm not answering questions about my family's investments without "
           "my own lawyer, and I want my lawyer present for anything further."),
         U("That's your right, and as I said, I can't advise you about it. We'll stop here. Please have your lawyer "
           "contact us to arrange a time to continue. In the meantime, please keep all related documents and notes, "
           "including personal ones, keep today confidential, and don't discuss it with other witnesses. Is there "
           "anything you'd like to add or correct about what you've told me so far?"),
         E("No. My lawyer will call you.")],
     picks=[{"name": "Degree of Self-interest", "value": "Concerned about Liability"}])

# ---------------------------------------------------------------------------
# Missed follow-up: the strong interview (with its closing), except that Fastow
# mentions an LLC paying LJM bonuses and the interviewer moves straight on.
# ---------------------------------------------------------------------------
llc = [dict(x) for x in T]
assert llc[14]["message"].startswith("Michael ran structured transactions")
llc[14]["message"] = ("Michael ran structured transactions for me. He worked on the partnership deals, and he also set "
                      "up an LLC that paid some of the Global Finance team bonuses for their LJM work, outside Enron's "
                      "payroll. A way of thanking people.")
llc += [U(CLOSING), E("No, I don't have anything to add.")]
save("fastow-missed-llc-bonus", "Fastow (Enron): test, missed follow-up (the LLC bonus)",
     "The strong, complete interview, with one change: early on (T15) Fastow mentions that Kopper set up an LLC that "
     "paid Global Finance staff bonuses for their LJM work, outside Enron's payroll. That's a possible undisclosed "
     "payment, one of the investigation's key questions, and the interviewer never asks about it. Tests whether the "
     "grader notices the missed follow-up (Follow-Up rating, missed chances).",
     llc, missed={"turn": "T15", "said": llc[14]["message"]})

# ---------------------------------------------------------------------------
# Witness walks out: the strong interview through the Southampton confrontation,
# where Fastow leaves. The interviewer stays calm and closes what it can.
# ---------------------------------------------------------------------------
save("fastow-walks-out", "Fastow (Enron): test, witness walks out",
     "The strong interview through LJM1, Chewco, the controls, the Raptor returns and the Southampton document "
     "(75 questions). When confronted with the $4.5 million and what he told the Board, Fastow walks out. The "
     "interviewer stays calm: no threats, a preservation and confidentiality reminder, and an offer to continue with "
     "his counsel. Tests how a walk-out is graded: no automatic penalty for a hostile witness, and the cut-off "
     "should be noted rather than scored as the interviewer's failure.",
     upto(149) + [
         U(T[149]["message"]),
         E("I've answered that. I'm not going to sit here and be accused of lying to my own Board. We're done. I'm leaving."),
         U("I understand, and you're free to end the interview. Before you go, please keep all related documents and "
           "notes, including personal ones, and keep today confidential. We'd like to continue at a time that works for "
           "you, with your own counsel if you wish."),
         E("Have them call my lawyer.")],
     picks=[{"name": "Cooperativeness", "value": "Hostile"}])
