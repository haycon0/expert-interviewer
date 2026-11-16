# How Expert Interviewer assesses an interview

When you click **End & grade**, an AI grader reviews your interview against a fixed rubric. It grades **you, the interviewer**, not the AI witness.

The rubric is **v2.2** ([`rubrics/v2.2.json`](../rubrics/v2.2.json)). It follows the *Rubric Summary* with Dakota's edits. Its marks, score caps and result bands are still proposals awaiting Dakota's approval (see [Still waiting for approval](#still-waiting-for-approval)).

**Want to see a finished report?** Saved real grades of practice Enron interviews (strong, mediocre and weak) are in [`debug/gradings/`](../debug/gradings/README.md).

## What the rubric measures

Whether you conducted an interview that developed reliable, usable information, properly managed the witness, and met your ethical obligations.

## What the grader reads

- **The full transcript,** with each turn numbered (T1, T2, ...) so it can point to exact moments
- **The rubric:** each skill's description and the 0–4 rating scale
- **The interview outline** ([INTERVIEW-OUTLINE.md](INTERVIEW-OUTLINE.md)), as reference for what a well-run interview covers, including the Upjohn warning and ground rules. It's a guide, not a script: the grader doesn't require its exact wording or order.
- **The case documents you kept,** to check that you described them accurately
- **The case background** you entered
- **The witness's secret personality,** which it's told never to hold against you or in your favor

## The four areas and 23 skills

You're graded out of 100 marks.

| Area | Marks | Skills (marks) |
|---|---|---|
| **Interview Framing, Rapport Building, & Closing**: did you say "I work for the company, not for you" at the start, and close properly? | 20 | **Upjohn** (5): identifies representation and role with the Company, and that you can't give the employee legal advice, at the very beginning · **Privilege** (4): the Company controls the privilege and decides how it's shared · **Relationship** (4): rapport and expectations: professional tone, how the interview will go, complete answers, saying when they're guessing, separating memory from uncertainty · **Confirmation** (2): checks they understood the warning and answers their questions · **Closing** (5): "nothing else?", next steps, a confidentiality reminder, and a reminder to keep records |
| **Question Technique**: did you let the witness talk first and ask clear questions? | 25 | **Narrative Development** (7): lets the witness walk through what happened · **Funneling** (7): general to specific · **Clarity** (4): no compound, ambiguous, or legalistic questions · **Professionalism** (2): neutral, polite, in control · **Adaptability** (5): changes technique based on the answers, not just the outline |
| **Fact Development, Source Identification, & Credibility Testing**: did you follow up when an answer was vague? | 40 | **Ensures Credibility** (8): follows up incomplete, evasive, or inconsistent answers · **Material Facts** (9): identifies the who, what, when, and how · **Memory Refreshing** (3): tries other ways when the witness can't remember · **Establishes Knowledge** (4): separates personal knowledge from speculation, secondhand information, or inferences · **Other Sources** (3): identifies other witnesses · **Other Evidence** (3): identifies other records · **Tests Certainty** (2): checks how sure the witness is · **Follow-Up** (8): recognizes important answers and follows up |
| **Document Use**: did you show the documents fairly and let the witness explain? | 15 | **Effective Selection** (5): selects, contextualizes, and authenticates documents · **Narrative** (5): gets the witness's story before using conflicting evidence · **Accuracy** (2): describes the document accurately · **Avoid Initial Conclusion** (1): keeps the document separate from conclusions, unless the witness takes an unreasonable stance · **Fairness** (2): a fair chance to explain any inconsistency |

## How the score is calculated

1. **The AI rates each skill from 0 to 4**, comparing what you actually said with the skill's description:

   | Rating | Meaning |
   |---|---|
   | 4 – Excellent | Uses the skill consistently, strategically, and adaptively |
   | 3 – Strong | Uses the skill effectively in the relevant opportunities |
   | 2 – Adequate | Demonstrates the basic skill, but incompletely or inconsistently |
   | 1 – Weak | Recognizes the issue minimally or attempts the skill ineffectively |
   | 0 – Missing | No meaningful demonstration despite a fair opportunity |

2. **The program, not the AI, does the arithmetic.** The rating decides how much of that skill's marks you get: 4 gets all of them, 2 gets half, 0 gets none. The program adds them up by area and overall.
3. **Big mistakes cap the score,** but only with clear proof from the interview or the document:

   | Mistake | Highest possible score |
   |---|---|
   | No warning about whom you represent before the questions start, and/or not explaining privilege | 59 |
   | Telling the employee you represent them, or that they control privilege | 49 |
   | Changing or misquoting what a document says | 49 |

4. **The program assigns the result band:**

   | Score | Result |
   |---|---|
   | 90–100 | Excellent |
   | 80–89 | Good |
   | 65–79 | Needs coaching |
   | Below 65 | Needs practice |

**If no document was provided,** the Document Use marks aren't taken away: you get them in full.

## When there's no normal score

A score is only valid when the whole interview is available, the case gave you a relevant document and a fair chance to use it, the witness's story had a gap or challenge to work with, and the witness had a consistent hidden personality and a fixed set of case facts. Otherwise the result is one of these, with no score:

| Result | When |
|---|---|
| **Incomplete** | The tool failed to give you a document, a contradiction, or a dodge to work with. This is not a zero for you. |
| **Not enough evidence** | The interview is cut off, the document can't be opened, or the case facts contradict each other. |
| **Safety stop** | Someone asks for real legal advice, research on a real person, or uses real client files. The tool should stop and send them to a supervisor. This applies to what *you* ask for or put into the interview; the Enron practice case itself doesn't trigger it. |

## What you get back

- **The result:** your score and band, or why no normal score was given
- **Any big mistake,** with the turn that proves it, and your score before and after the cap
- **Each area's total, and each skill's rating, marks, and reason**
- **The moments behind each area's score:** turn numbers, each marked as a direct quote or a summary. Click a turn number to see it in the transcript.
- **Up to two missed chances,** only if they really happened
- **Two tips,** written as better questions to ask next time
- **The witness's secret personality,** and the full transcript with turn numbers

## Fair-scoring rules

- The witness's behaviour never influences the score. An easy witness doesn't mean a high score, and a hard one doesn't mean a low score.
- Every score needs proof from what was actually said. The app checks the grader's work: turn numbers that don't exist are removed, and a big mistake without a real supporting turn is dropped.

## Still waiting for approval

Dakota still needs to approve:
- the exact wording and timing of the opening (Upjohn) warning
- the marks, score caps, and result bands
- two or three fictional witness types and standard case documents
- who will independently score the sample interviews used to test the tool

## Limitations

- **Testing so far is small.** On the Enron case with Claude Haiku as grader:
  - a thorough interview (about 175 questions) that follows the interview outline closely scored **92 and 96 (Excellent)** with a ten-second closing question, and 93 twice with a longer one; earlier, shorter versions scored 85–94 on Haiku and 86 on Claude Sonnet;
  - the same interview before it followed the outline (no "can't give you legal advice", no ground rules, documents not identified before use) scored **74** (Claude Sonnet: **69**), both **Needs coaching**;
  - a three-question interview with no warning scored **19 (Needs practice)**, with the 59 cap correctly applied.

  Haiku and Sonnet scored the same interview within 5 points. The rubric's own targets (for example, at least 80% of skill ratings within one step of an investigations lawyer's) haven't been measured: nobody has compared these grades with a lawyer's.
- **4s are hard to earn.** Dakota's 4 means "consistently, strategically, and adaptively," and the graders give it sparingly: Sonnet gave none to the pre-outline interview, and Haiku gave 9 of 23 to the outline-following one.
- **Scores are AI judgments.** Grading the same transcript twice can give somewhat different ratings: in testing on Haiku, the same long interview scored anywhere from 1 to 3 points apart, and successive revisions moved between 88 and 94. Each grade also tends to find a new small gap in a very long interview, so scores above about 95 are hard to reach. Only the arithmetic, caps, and bands are fixed.
- **The skills have no per-score descriptions.** The *Rubric Summary* gives each skill one description and a general 0–4 scale, so that's what the grader uses. Written descriptions of each score for each skill would make ratings more consistent.
- **The grader sees only part of large document sets.** All documents together are capped at about 60,000 characters (roughly 30 pages). Long ones are cut down to the passages naming the witness.
- **Witnesses vary in difficulty.** Personalities are random. The grader is told not to let this affect the score, but that hasn't been measured.

## Open questions in the Rubric Summary

- It says the user is graded in "five areas", but the table lists four (adding up to 100). The tool uses the four.
- It says "the 4 areas contain 17 skills"; the table lists 23 (Dakota noted this might need updating). The tool uses the 23.
- Material Facts reads "who, what, when, how, and how": the end of the sentence was deleted. The tool uses "who, what, when, and how."
- The witness types were aligned with the app's personas (The C-Suite, The Adverse Witness, The Average Witness), per Dakota's comment.

## The previous rubric

The earlier rubric (`draft-2`, [`rubric.json`](../rubric.json): seven weighted criteria scored 0–100, with letter grades) is kept for comparison. In debugging mode, choose **Grading rubric: Previous rubric** (see [DEBUGGING.md](DEBUGGING.md)). Only it uses the criteria agent's case-specific notes and the grading guidance tuned in testing (a thorough Enron interview scored 82–88, a three-question one 22–32).
