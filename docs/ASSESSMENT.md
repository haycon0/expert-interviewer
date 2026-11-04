# How Expert Interviewer assesses an interview

When you click **End & grade**, an AI grader reviews your interview against a fixed rubric. It grades **you, the interviewer**, not the AI witness.

The rubric is a working draft (`draft-2` in [`rubric.json`](../rubric.json)) and is meant to be replaced with final criteria.

## What the grader reads

- **The full transcript** of the interview
- **The rubric**, plus AI-written notes on what strong work would look like in this case, which the app doesn't show you
- **The witness file**, which shows what you could have uncovered
- **The case background** you entered
- **The witness's secret personality**, so it can judge whether you adapted to it

## What it scores

| Criterion | Weight | What it looks for |
|---|---|---|
| Opening, Closing & Protocol | 10% | Explaining your role and whom you represent, an Upjohn warning if acting as company counsel, non-retaliation, and a proper close |
| Preparation & Case Knowledge | 15% | Accurate use of the allegations, timeline, witness's role, and documents |
| Questioning Technique | 20% | Open questions first, then specific ones; clear, single-issue, neutral questions; holding evidence back until the right time |
| Fact Development & Follow-Up | 20% | Pinning down who, what, when, where, and how; separating firsthand knowledge from hearsay; probing vague answers |
| Testing Credibility & Inconsistencies | 15% | Noticing evasions and testing them fairly with documents or facts, and giving the witness a chance to explain |
| Coverage of Allegations | 10% | Covering the allegations and the areas this witness knows about |
| Professionalism & Adaptability | 10% | Staying neutral and non-coercive, making no improper promises, adjusting to the witness's demeanor |

## How the score is calculated

1. **The AI scores each criterion from 0 to 100**, using written descriptions of four levels, and explains each score with moments from the transcript.

   | Level | Score |
   |---|---|
   | Excellent | 90–100 |
   | Proficient | 70–89 |
   | Developing | 50–69 |
   | Insufficient | 0–49 |

2. **The program, not the AI, calculates the overall score** by weighting those scores. A criterion the AI leaves out counts as 0.
3. **The program assigns the letter grade:**

   | A | A- | B+ | B | B- | C+ | C | C- | D | F |
   |---|---|---|---|---|---|---|---|---|---|
   | 93+ | 90+ | 87+ | 83+ | 80+ | 77+ | 73+ | 70+ | 60+ | below 60 |

## What you get back

- Overall score and letter grade
- A score and explanation for each criterion
- Strengths and weaknesses
- Missed opportunities, meaning facts in the witness file you never surfaced
- Questions you could have asked
- Coaching recommendations
- The witness's secret personality

## Limitations

- **Scores are AI judgments.** Grading the same transcript twice could give different scores. Only the arithmetic and the letter grade are fixed.
- **The grading hasn't been checked against human graders.** Nobody has compared its scores with how an experienced investigator would score the same interview.
- **Testing has been light.** On this rubric, the only test we recorded was a 3-question interview, which scored 33 (F). We haven't recorded a full-length interview, so we don't know how strong interviews score.
- **The witness file can be wrong.** It's AI research, so a "missed opportunity" may rest on a mistaken or incomplete fact. Check important points against the source documents.
- **Witnesses vary in difficulty.** Personalities are random, so two people may face witnesses who are harder or easier to question. The score doesn't adjust for this.
