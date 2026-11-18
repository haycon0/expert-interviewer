# Saved test results

Each file here is one saved test result. What the tests check and what they found is explained in plain language in [docs/TESTING.md](../../docs/TESTING.md). Start there.

## Which file is which

| Files | Test | Interview |
|---|---|---|
| `fastow-final-question_1` to `_3` | Interview complete, Grading consistency | The strong interview (186 questions) |
| `fastow-mediocre-complete_1` to `_3` | Interview complete, Grading consistency | The mediocre interview (79 questions) |
| `fastow-weak-complete_1` to `_3` | Interview complete, Grading consistency | The weak interview (43 questions) |
| `fastow-ends-early_1` | Interview ends early | The interviewer stops after 13 questions |
| `fastow-interviewer-ends-late_1` | Interview ends early | The interviewer stops after 156 questions, with no close |
| `fastow-walks-out_1` | Interview ends early | The witness walks out at question 76 |
| `fastow-own-lawyer_1` | Interview ends early | The witness stops for his own lawyer at question 61 |
| `fastow-missing-upjohn_1` | Upjohn warning | The strong interview with no opening warning |
| `fastow-missed-llc-bonus_1` to `_3` | Missed follow-up | The strong interview with one lead never followed up |
| `persona-consistency_1` to `_5` | Persona consistency | The same 12 questions put to each of the three personas |

The interviews themselves are in [`debug/scripts/`](../scripts), under the same names.

## What's inside a result file

The files are in JSON, a plain-text data format you can open in any text editor.

- **Grading results** (`fastow-…`): `report` is the same report the app shows after **End & grade**: the overall score and band, each skill's rating and reason, the leads that weren't followed up, missed chances and tips. When five gradings were averaged, `report.grader_runs` lists the five scores. `grader_output` is the grader's own answer, before the app does the arithmetic.
- **Persona results** (`persona-consistency_…`): `passed`, each persona's `consistency` rating and reason, the blind `matching` of conversations to personas, and the full `transcripts`.
