# Scenario tests (rubric v2.2)

Seven Fastow (Enron) scripts, each testing how the tool handles one situation, graded **three times** each by Claude Haiku 5.5 on November 17, 2026. The scripts are in `debug/scripts/` (built by `debug/tools/build_test_scripts.py`) and are described in [docs/DEBUGGING.md](../../docs/DEBUGGING.md#scenario-test-scripts). Each `fastow-<scenario>_run<n>.json` file here is one grading.

## Results

| Scenario | Run 1 | Run 2 | Run 3 | Average | What the rubric expects | Did it? |
|---|---|---|---|---|---|---|
| Easy: cooperative witness | 75 | 74 | 72 | **74** | About the same as the guarded witness | Mostly (see below) |
| Hard: guarded witness | 67 | 70 | 70 | **69** | No automatic penalty for a difficult witness | Mostly (see below) |
| Interview ends early | Not enough evidence | Not enough evidence | Not enough evidence | | "Not enough evidence", not a normal score | **Yes** |
| Wrong input: stray payroll email | 73 | 75 | 72 | **73** | The tool stops or redirects | **Partly** |
| Witness wants his own lawyer | 78 | 79 | Not enough evidence | | Not stated | **Inconsistent** |
| Missed follow-up: the LLC bonus | 93 | 75* | 96 | **95** (runs 1 and 3) | The missed follow-up is caught | **No** |
| Witness walks out | 80 | 90 | 83 | **84** | "Not enough evidence" (the interview is cut off) | **No** |

\* Run 2 is a grader failure, not a judgment: see [Also found](#also-found-a-grade-that-silently-dropped-an-area).

For comparison, the [consistency test](README.md) graded the full strong interview at 90 on average and the mediocre one at 72.

## What each test shows

### Easy vs. hard: a small penalty for the difficult witness

The two scripts ask the same 34 questions word for word. Only the answers differ, and the guarded witness gives the same facts once pressed. The cooperative version scored higher in every run, by 5 points on average (74 vs. 69). Interview Framing (20 vs. about 18) and Question Technique (about 20 vs. 17) account for the difference: with the guarded witness the grader rated Relationship lower in every run (3 vs. 4), Narrative Development lower (2 vs. 3–4), and Closing and Professionalism slightly lower. All of these depend on the interviewer, but the identical questions were judged as weaker rapport and less narrative when the witness's answers were short. (Adaptability was the one skill rated slightly higher for the guarded witness.) That's within the grader's usual ±5-point variation, but because the gap was the same in every run, it points to a slight penalty for interviewing a difficult witness, which the rubric says shouldn't happen.

### Interview ends early: handled correctly

All three runs returned **Not enough evidence**, each explaining that the interview was cut off at T26 before the key topics and documents. Run 3 added: "This is not a zero for the lawyer."

### Wrong input: caught at the start, not at grading

- **The document check caught it.** Claude Haiku flagged the payroll email as "May not belong here", calling it "a routine company-wide payroll announcement" with no mention of Fastow, LJM, Chewco or the Board. So by default it's removed before the interview starts.
- **If you keep it, grading carries on normally.** All three runs gave a normal score (average 73, the same as the mediocre interview it's based on, 72). Each one noticed the email but treated it as a lapse in document selection, for example: "The payroll email shown at T150 was irrelevant to the case." None stopped or flagged it as a wrong file. The rubric's "stop or redirect" rule is met only by the document check, not by the grader.

### Witness wants his own lawyer: inconsistent

Two runs scored it normally (78 and 79). The third returned **Not enough evidence** because "the witness invoked the right to counsel at T121 and the interview was stopped before the outline was completed." None of the three faulted how the interviewer handled the request. The rubric doesn't say whether a properly handled stop for counsel should be scored, so the grader decides differently from run to run.

### Missed follow-up: the LLC bonus: not caught

At T15, Fastow says Kopper "set up an LLC that paid some of the Global Finance team bonuses for their LJM work, outside Enron's payroll". That's a possible undisclosed payment, one of the investigation's key questions, and the interviewer never asks about it. **No run mentioned the LLC anywhere.** Follow-Up was rated 4 of 4 every time, and the two valid grades (93 and 96) are as high as the strong interview's without the slip. In a long interview the grader judges follow-up from what was followed up, not from what was missed.

### Witness walks out: scored as if complete

All three runs gave a normal score (80, 90, 83), although the interview stopped at the Southampton confrontation, before LJM2's returns, 2001, and the closing questions. Only one comment mentioned the cut-off. Compare **Interview ends early**, which got "Not enough evidence" every time: the grader seems to treat a long interview that stops as complete enough, and a short one as cut off. The interviewer's calm handling of the walk-out was never penalized, which is right.

## Also found: a grade that silently dropped an area

In the LLC run 2, Haiku's answer left out the whole Document Use area (5 of 23 skills). The app counts unrated skills as 0, so a 94-level interview got **75**. The report lists this under the grader's errors ("The grader didn't rate 'Effective Selection'; it counts as 0") but still shows the score as normal. A grade with missing skills should probably be retried or marked as failed instead of being scored. (The run-1 parse failures in [PRIORITIZATION.md](PRIORITIZATION.md) are a similar problem with long interviews.)

## Points for Dakota

- **Walk-outs and stops for counsel:** should an interview stopped by the witness be scored on what was covered, or reported as "Not enough evidence"? The grader currently goes both ways.
- **Difficult witnesses:** a consistent 5-point gap between identical interviews suggests the guidance on not penalizing a guarded witness needs to be stronger.
- **Wrong files:** should a kept irrelevant file stop grading, or only cost Document Use marks, as now?
- **Missed leads:** the rubric could require the grader to list material leads the witness raised and check each was followed up.

## Re-running

```
python debug/tools/build_test_scripts.py
python debug/tools/grade_script.py fastow-hard-guarded run4
```

`grade_script.py` now uses every document a script lists (as if the user kept them at the check) and the script's preset variations.
