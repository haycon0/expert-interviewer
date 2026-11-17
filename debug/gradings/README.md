# Grading consistency test (rubric v2.2)

Three complete Fastow (Enron) interviews of different quality, each graded **three times** by the same grader, to show how consistent the grading is. Each JSON file in this folder is one grading: the full score report plus the grader's raw output.

- **Grader:** Claude Haiku 5.5, rubric v2.2, graded on November 15, 2026. All nine gradings together cost about 15 cents.
- **Persona:** The C-Suite, no variations, for all three interviews.
- **Same input every time:** the transcript, documents and prompt were identical across a script's three runs. Only the grader's own variation differs.

## Results

| Interview | Script | Questions | Run 1 | Run 2 | Run 3 | Average | Spread |
|---|---|---|---|---|---|---|---|
| **Strong** | `fastow-final-question` + its closing question | 178 | 96 | 90 | 84 | **90** (Excellent) | 12 |
| **Mediocre** | `fastow-mediocre-complete` | 79 | 78 | 70 | 69 | **72** (Needs coaching) | 9 |
| **Weak** | `fastow-weak-complete` | 43 | 65 | 66 | 67 | **66** (Needs coaching) | 2 |

(The strong script leaves its closing question for the user, so these runs add the question from [`fastow-final-question-closing.md`](../scripts/fastow-final-question-closing.md) and the witness reply "No, I don't have anything to add.")

## What this shows

- **The ranking never changed.** In every run, strong scored above mediocre and mediocre above weak. The lowest strong grade (84) beat the highest mediocre grade (78), which beat the highest weak grade (67).
- **No skill rating moved by more than one step.** Across a script's three runs, 7–10 of the 23 skills changed rating, always by exactly one step (for example 4 → 3). The rubric's target is at least 80% of ratings within one step of an investigations lawyer's. These runs show the grader is within one step of *itself*. Nobody has compared it with a lawyer yet.
- **Overall scores swing more than the ratings suggest.** A one-step change on a high-mark skill moves the total a lot: Material Facts (9 marks) or Ensures Credibility and Follow-Up (8 marks) shift 2–2.25 points each. When several of those move together the total can shift 6–12 points, as in the strong interview (96 → 84).
- **Better interviews vary more.** The weak interview was consistent (spread 2): its gaps are obvious. In the strong one, the grader keeps judging whether a good performance is "consistent" enough for a 4, and those 3-versus-4 calls account for the whole spread.
- **Practical takeaway:** treat a single grade as about ±5 points. To compare interviews or settings, grade more than once and average.

## Skills whose rating changed between runs

| Interview | Skills (ratings in runs 1, 2, 3) |
|---|---|
| Strong | Narrative Development 4-4-3 · Adaptability 4-3-3 · Ensures Credibility 4-3-3 · Material Facts 4-4-3 · Memory Refreshing 4-3-3 · Follow-Up 4-3-3 · Narrative 4-4-3 |
| Mediocre | Upjohn 4-3-3 · Privilege 4-3-3 · Confirmation 2-3-2 · Narrative Development 4-3-3 · Memory Refreshing 3-2-2 · Tests Certainty 3-3-2 · Follow-Up 4-3-3 · Effective Selection 3-2-2 · Accuracy 4-3-3 · Fairness 4-3-3 |
| Weak | Confirmation 1-2-2 · Adaptability 3-2-3 · Other Evidence 3-3-2 · Tests Certainty 2-3-2 · Follow-Up 2-3-3 · Avoid Initial Conclusion 1-1-2 · Fairness 3-2-3 |

## How the weak and mediocre interviews differ from the strong one

Both were made from the strong script's exchanges, with parts removed or reworded:

- **Mediocre:**
  - a sound Upjohn warning, but no ground rules and no answer to his question about his own counsel
  - the main topics with some open questions
  - documents shown without first identifying or authenticating them
  - few "how do you know" or certainty questions
  - a short close
- **Weak:**
  - a bare-bones warning: no "can't give legal advice", and no explanation that the company decides whether to waive
  - no ground rules
  - several leading or compound questions
  - little follow-up
  - documents put to him before his own account
  - an abrupt close

Both scripts are in `debug/scripts/` and appear in the Debugging box. They're complete, so you can click **End & grade** straight away.

## Rubric gap: prioritization and use of time

`fastow-poor-prioritization_run*.json` grade the strong interview with a 31-question detour into low-value topics. They scored 94, 87, 89 (average 90, the same as without the detour). See [PRIORITIZATION.md](PRIORITIZATION.md).

## Scenario tests

Seven more scripts (cooperative vs. guarded witness, an interview that ends early, a stray payroll email, a witness who wants his own lawyer, a missed follow-up, and a walk-out), each graded three times. See [SCENARIOS.md](SCENARIOS.md).

## Re-running

From the project folder, with an API key in `.env`:

```
python debug/tools/grade_script.py fastow-weak-complete run4
python debug/tools/grade_script.py fastow-final-question run4 --strong-closing
```

Add a model such as `anthropic:claude-sonnet-5-5` to use a different grader. `debug/tools/build_tier_scripts.py` rebuilds the weak and mediocre scripts from the strong one.
