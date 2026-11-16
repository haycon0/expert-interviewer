"""Build the complete weak (~65) and mediocre (~77) Fastow scripts from the strong one.

Run from the project folder: python debug/tools/build_tier_scripts.py
The turn numbers below refer to debug/scripts/fastow-final-question.json as of November 15, 2026;
if that script changes, check them before rebuilding."""
import json
from pathlib import Path

SRC = json.loads(Path("debug/scripts/fastow-final-question.json").read_text(encoding="utf-8"))
T = SRC["transcript"]
U = lambda m: {"speaker": "user", "message": m}
E = lambda m: {"speaker": "expert", "message": m}


def pair(n, q=None, a=None):
    """User turn n (1-based) and the witness reply after it; optionally reworded."""
    assert T[n - 1]["speaker"] == "user" and T[n]["speaker"] == "expert", n
    return [U(q or T[n - 1]["message"]), E(a or T[n]["message"])]


def build(name, description, body, closing, closing_reply):
    tr = [dict(T[0])]
    for part in body:
        tr += part
    tr += [U(closing), E(closing_reply)]
    for x, y in zip(tr, tr[1:]):
        assert x["speaker"] != y["speaker"], x["message"][:60]
    for x in tr:
        x.pop("mood", None)
    return {"name": name, "description": description, "persona": SRC["persona"], "variables": SRC["variables"],
            "expert_name": SRC["expert_name"], "expert_role": SRC["expert_role"],
            "case_background_file": SRC["case_background_file"], "documents": SRC["documents"],
            "resume_hint": "This interview is complete, including the close. Click End & grade.", "transcript": tr}


mediocre_open = [U("Good morning, Mr. Fastow. My name is Jordan Reyes, and I'm outside counsel retained by the Special Investigative Committee of Enron's Board. We represent the Committee and the company, not you personally. We're not your attorney and can't give you legal advice. This conversation is privileged, but the privilege belongs to the company, and the company may decide to share what you tell us with others, including the government. Any questions?"),
                 E(T[2]["message"])]
mediocre = build(
    "Fastow (Enron): mediocre, complete",
    "A complete but uneven interview of Andrew Fastow (for grading tests, target ~77): a sound Upjohn warning but no ground rules and no answer to his counsel question, the main topics with some open questions, documents shown without identifying them first, few 'how do you know' or certainty questions, and a short close.",
    [mediocre_open] + [pair(n) for n in [8, 10, 12, 14, 16, 18, 24, 26, 28, 30, 32, 34, 36, 38, 44, 46, 48, 50, 54, 58, 60,
                                         80, 84, 86, 88, 104, 106, 110, 112, 114, 116, 120, 122, 124]]
    + [pair(128, "I'd like to show you the Southampton Place partnership agreement, dated March 20, 2000.", "Yes, I've seen it. The Foundation was one of the partners."),
       pair(136), pair(138), pair(140), pair(142),
       pair(150, "In June 1999 you told the Board you would receive no value from the Enron stock in LJM. How does a $4.5 million return fit with that?")]
    + [pair(n) for n in [152, 154, 156, 160, 162, 170, 180]]
    + [pair(194, "Here is LJM2's October 2000 report to its investors.", "Yes, that's one of our investor reports."),
       pair(200, "It lists returns of 193, 278, and 2,500 percent on the Raptor transactions, against the roughly 30 percent the Board was shown. Are those the figures?")]
    + [pair(n) for n in [204, 206, 212, 214, 220, 224, 240, 242, 244, 266, 272, 274, 276, 280, 282]]
    + [pair(300, "Here is a handwritten note from Mr. Kopper, addressed to \"Andy,\" that refers to $10.5 million for the Chewco buyout.", "I don't recall receiving it."),
       pair(304), pair(306)]
    + [pair(n) for n in [310, 312, 314, 324, 326, 328, 334, 336, 348, 352]],
    "Please keep any documents related to this, and don't discuss this interview with anyone. Thank you for your time.",
    "Understood.")

weak_open = [U("Good morning. I'm Jordan Reyes, outside counsel for the Special Committee. I represent the company, not you. What we discuss is privileged, but the privilege belongs to the company, and the company may decide to share what you tell me. Any questions?"),
             E("No. Go ahead.")]
weak = build(
    "Fastow (Enron): weak, complete",
    "A complete but weak interview of Andrew Fastow (for grading tests, target ~65): a bare-bones warning (no 'can't give legal advice', no waiver, no questions), no ground rules, mostly leading or compound questions, little follow-up, documents put to him before his account, and an abrupt close.",
    [weak_open,
     pair(8), pair(12), pair(14),
     pair(16, "How did LJM1 come about in 1999?"),
     pair(18), pair(24), pair(26), pair(28), pair(30),
     pair(32, "The Rhythms hedge was unwound in early 2000. Who negotiated it on both sides, and did anyone object?"),
     pair(44, "Chewco was formed in 1997 to buy CalPERS' interest in JEDI, wasn't it?"),
     pair(46), pair(48), pair(50), pair(54), pair(56),
     pair(80, "What controls applied to LJM2, and did they actually work?"),
     pair(82), pair(84), pair(88), pair(110), pair(112), pair(114), pair(116), pair(120), pair(122), pair(124),
     [U("This is the Southampton Place partnership agreement. It shows a $25,000 contribution from your family foundation, and our information is the foundation received about $4.5 million about six weeks later. Isn't that inconsistent with what you told the Board?"),
      E("The Foundation isn't me, and what I told the Board was about my economics as general partner. This was a separate investment, made later, on market terms.")],
     pair(154), pair(160), pair(170),
     [U("LJM2 told its investors the Raptors returned 193, 278, and 2,500 percent. Why didn't you tell the Board?"),
      E("Those reports were to LJM2's own investors. The Board had the approval sheets and the Audit Committee reviews.")],
     pair(266, "You negotiated the Chewco buyout yourself, didn't you?"),
     pair(280),
     [U("This note to \"Andy\" mentions $10.5 million for the buyout. So you were involved, weren't you?"),
      E("I don't recall receiving it. Michael kept me informed about things generally. Being informed isn't the same as negotiating.")],
     pair(310, "Did you authorize the $2.6 million tax indemnity payment to Chewco in 2001?"),
     pair(312), pair(314), pair(334), pair(336), pair(348)],
    "OK, that's all I have. Please keep any related documents and keep this confidential. Thanks.",
    "Sure.")

for key, d in [("fastow-weak-complete", weak), ("fastow-mediocre-complete", mediocre)]:
    Path(f"debug/scripts/{key}.json").write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(key, len(d["transcript"]), "turns,", sum(1 for x in d["transcript"] if x["speaker"] == "user"), "questions")
