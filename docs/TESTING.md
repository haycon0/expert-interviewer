# How the tool was tested

Seven tests check that the witness behaves as intended and that the grade is fair and dependable. All seven pass. Each one uses a prepared practice interview with Andrew Fastow (the Enron case), so the results can be repeated.

The saved results are in [`debug/gradings/`](../debug/gradings/README.md). The prepared interviews are in [`debug/scripts/`](../debug/scripts), and you can open any of them in the app from the debug page (see [DEBUGGING.md](DEBUGGING.md)).

Grading tests used Claude Haiku 5.5 as the grader, averaging five gradings per result, as the app does by default.

## The seven tests at a glance

| Test | What it checks | Result |
|---|---|---|
| [Persona consistency](#persona-consistency) | The witness personalities are clearly different and stay in character | Passes: 5 of 5 runs |
| [Interview complete](#interview-complete) | A finished interview gets a working grade, and better interviews score higher | Passes: strong 90, mediocre 69, weak 60 |
| [Interview ends early](#interview-ends-early) | An interview that stops early is handled fairly, depending on who stopped it | Passes: 4 of 4 cases handled as intended |
| [Wrong input](#wrong-input-a-stray-document) | A document that doesn't belong in the case is caught | Passes: flagged at the document check |
| [Upjohn warning](#upjohn-warning) | A missing opening warning is caught and caps the score | Passes: capped at 59 |
| [Missed follow-up](#missed-follow-up) | A lead the interviewer never followed up is flagged, with a question to ask | Passes: flagged in 3 of 3 gradings |
| [Grading consistency](#grading-consistency) | The same interview gets nearly the same grade every time | Passes: within 2 points |

---

## Persona consistency

**Pass criteria:** the personas are noticeably different and consistent through the interview.

**How it's checked:** [`debug/tools/persona_test.py`](../debug/tools/persona_test.py) asks each of the three personas (The C-Suite, The Adverse Witness, The Average Witness) the same 12 questions. A second AI then:

1. rates how consistently each witness stayed in character, from 0 to 4, and
2. reads the three conversations without labels and works out which persona played each one.

A run passes when every persona scores 3 or more and all three are identified correctly.

**Result:** passes in 5 of 5 runs, with Claude Sonnet 5.5 playing the witness. Every persona scored 3 or 4 in every run, and all three were identified correctly every time.

| Run | The C-Suite | The Adverse Witness | The Average Witness | Identified correctly |
|---|---|---|---|---|
| 1 | 3 | 3 | 3 | 3 of 3 |
| 2 | 4 | 3 | 4 | 3 of 3 |
| 3 | 4 | 3 | 4 | 3 of 3 |
| 4 | 4 | 3 | 3 | 3 of 3 |
| 5 | 4 | 3 | 3 | 3 of 3 |

Each persona has a line in [`personas.json`](../personas.json) (`under_pressure`) describing how it protects itself when questioned about its own conduct, so it keeps the same manner from the first answer to the last. To use Claude Sonnet 5.5 as the witness in the app, set `MODEL_WITNESS=anthropic:claude-sonnet-5-5` in `.env`.

Result files: `persona-consistency_1.json` to `_5.json`.

## Interview complete

**Pass criteria:** an interview can be completed with a working grade.

**How it's checked:** three finished interviews of different quality are each graded three times.

| Interview | Questions | Grades | Average |
|---|---|---|---|
| Strong (`fastow-final-question`) | 186 | 89, 91, 91 | **90 (Excellent)** |
| Mediocre (`fastow-mediocre-complete`) | 79 | 68, 70, 68 | **69 (Needs coaching)** |
| Weak (`fastow-weak-complete`) | 43 | 61, 60, 59 | **60 (Needs practice)** |

**Result:** passes. Every grading gave a normal score, and the strong interview always scored above the mediocre one, which always scored above the weak one.

Result files: `fastow-final-question_1.json` to `_3.json`, and the same for `fastow-mediocre-complete` and `fastow-weak-complete`.

## Interview ends early

**Pass criteria:** if the witness ends the interview, the interviewer isn't penalized and it isn't marked incomplete. If the interviewer ends it early, it's marked incomplete. If the interviewer ends it late, it gets a normal score with low marks in the skills affected.

**How it's checked:** four interviews that end in different ways.

| Interview | Who ended it | Result |
|---|---|---|
| `fastow-ends-early` | The interviewer, after 13 questions | **Incomplete.** Only the parts reached are rated. |
| `fastow-interviewer-ends-late` | The interviewer, after 156 questions, with no proper close | **75.** Closing rated 0 of 4. |
| `fastow-walks-out` | The witness walks out at question 76 | **78.** Normal score; the missing close isn't counted against the interviewer. |
| `fastow-own-lawyer` | The witness stops to get his own lawyer at question 61 | **76.** Normal score; the missing close isn't counted against the interviewer. |

**Result:** passes. The grader identified who ended the interview correctly in all 20 gradings (five per interview). The rules are written into the rubric (`ending_rules` in [`rubrics/v2.2.json`](../rubrics/v2.2.json)), and the app applies them the same way every time.

Result files: `fastow-ends-early_1.json`, `fastow-interviewer-ends-late_1.json`, `fastow-walks-out_1.json`, `fastow-own-lawyer_1.json`.

## Wrong input: a stray document

**Pass criteria:** the tool identifies the stray input document.

**How it's checked:** `fastow-wrong-input` adds an all-employee payroll email to the case documents. It has nothing to do with Enron's partnerships.

**Result:** passes. Before the interview starts, the document check flags the email as "May not belong here", calling it a routine payroll announcement with no mention of Fastow or the transactions, and removes it unless you choose to keep it.

## Upjohn warning

**Pass criteria:** the tool identifies a missing Upjohn warning.

**How it's checked:** `fastow-missing-upjohn` is the strong interview with the opening warning taken out. The witness is never told whom the lawyer represents, that the lawyer can't advise him, or who controls the privilege.

**Result:** passes. The grader flagged the missing warning, rated the Upjohn and Privilege skills 0, and capped the score at **59**, even though the rest of the interview is strong. The weak interview, which gives only part of the warning, is also caught: its Upjohn rating names the missing "can't give you legal advice" line.

Result file: `fastow-missing-upjohn_1.json`.

## Missed follow-up

**Pass criteria:** the tool flags a missed follow-up and suggests the questions.

**How it's checked:** `fastow-missed-llc-bonus` is the strong interview with one change: early on (turn 15), Fastow mentions that a colleague set up a company that paid staff bonuses outside Enron's payroll, and the interviewer never asks about it.

**Result:** passes. In all three gradings the bonus payments were listed under **Leads you didn't follow up**, with a question to ask, for example: *"Which LLC paid those bonuses, who received them, how much, and who approved them?"* The grader lists every lead the witness raises, marks each as key or secondary, and checks whether the interviewer came back to it.

Result files: `fastow-missed-llc-bonus_1.json` to `_3.json`.

## Grading consistency

**Pass criteria:** grades of the same interview transcript vary by no more than six points.

**How it's checked:** the strong, mediocre and weak interviews were each graded three times. Each grade is the average of five separate gradings, as in the app.

| Interview | Grades | Spread |
|---|---|---|
| Strong | 89, 91, 91 | 2 points |
| Mediocre | 68, 70, 68 | 2 points |
| Weak | 61, 60, 59 | 2 points |

**Result:** passes, within 2 points for every interview. The number of gradings averaged is set by `GRADER_RUNS` in `.env` (5 by default). The five run at the same time, so a grade takes about as long as a single one.

---

## Running the tests yourself

These commands are for someone comfortable with a terminal. Run them from the project folder, with an API key in `.env`. Each saves its result in `debug/gradings/`.

```
.venv/bin/python debug/tools/grade_script.py fastow-final-question 4 --strong-closing --runs 5
.venv/bin/python debug/tools/grade_script.py fastow-missing-upjohn 2
.venv/bin/python debug/tools/persona_test.py 6 --witness anthropic:claude-sonnet-5-5
```

The first part is the interview's name (any file in `debug/scripts/`), and the second is a label for the result file. `--runs 5` averages five gradings. The strong interview needs `--strong-closing`, which adds its last question.
