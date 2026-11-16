# Rubric gap: prioritization and use of time

**The gap:** rubric v2.2 scores *how* each question is asked, but never whether the interview spent its time on what matters. Real witness interviews are time-limited, and executives especially may give an hour or two. A lawyer would expect the interviewer to reach the central allegations early and not spend a large share of the interview on low-value topics. The rubric has no skill, score cap, or "coverage" measure for this. Funneling (7 marks) asks only whether questions move "in a sensible order from general to specific", and every other skill rewards good technique wherever it's used, including on irrelevant topics.

## The example

[`debug/scripts/fastow-poor-prioritization.json`](../scripts/fastow-poor-prioritization.json) is the strong Fastow interview, complete with its closing question, plus a **31-question detour (T32–T93)** placed right after the June 28, 1999 Board meeting. The detour comes before the Rhythms unwind, Chewco, LJM2, Southampton and every other key issue. Nothing else changes.

The detour covers other items from the same Board meeting and the Global Finance group:

| Topic | Questions | Relevance to the investigation |
|---|---|---|
| The Falcon 900EX aircraft lease (financing bank, guarantee, users, cost, where the documents are) | 13 | None: a routine item Fastow presented |
| The two-for-one stock split (approval, transfer agent, timing) | 6 | None |
| The Gaza power project (structure, equity split, return, Board approval) | 7 | None |
| Global Finance headcount, recruiting, office location, budget | 5 | Background at most |

The detour is deliberately *well run*: open invitations, follow-ups, "how sure are you?" and "how do you know?" questions. It's 31 of 210 questions (15%), and it delays every central issue.

The script appears in the Debugging box as **Fastow (Enron): strong, with poor prioritization**. It's complete, so you can click **End & grade** straight away.

## Results (Claude Haiku 5.5, three runs each, November 15, 2026)

| | Run 1 | Run 2 | Run 3 | Average | Band |
|---|---|---|---|---|---|
| Strong interview | 96 | 90 | 84 | 90 | Excellent |
| **Same interview + 31-question detour** | **94** | **87** | **89** | **90** | **Excellent / Good** |

Funneling, the only skill touching on order, was rated 3 in all three runs. The strong interview also got a 3 on Funneling in its last two gradings.

## What this shows

- **No penalty at all.** The average is identical (90 vs. 90), and the detour version's best grade (94) came close to the strong interview's best (96).
- **The grader treated the detour as good work.** It cited detour questions as *evidence* for the scores:
  - "Tell me everything you remember about the aircraft lease" (T34), as an open invitation
  - "How do you know the guarantee fell under that policy" (T48), for Establishes Knowledge
  - "How sure are you about the bank and the date?" (T40) and "How certain are you of that?" (T64), for Tests Certainty
- **It even asked for more time on the irrelevant topic.** One run's missed chances faulted the interviewer for not pressing harder on who negotiated the aircraft financing and for not asking for the lease documents (T45).
- **Only one comment in three runs noticed anything,** and only as a sequencing issue: "moving from the aircraft lease to the stock split and Gaza [was] abrupt rather than building toward the central issues." It didn't lower the score beyond the 3 that Funneling usually gets.

## Also found: long interviews can fail to grade

The first attempt at run 1 failed twice before succeeding. Haiku's answer either left out the "tips" section or came back cut off and garbled, probably because this 419-turn interview produced a very long grade. In the app, that shows as "Grading didn't finish" and the user has to click **End & grade** again. Very long interviews may need a stronger grader, a higher output limit, or a schema that tolerates a missing section.

## How the rubric could address it (not changed; for Dakota to decide)

- **A prioritization skill**, for example under Question Technique: "Reaches the central allegations early and spends time in proportion to their importance."
- **A coverage measure:** list the key topics for each case and check whether, and how early, each was reached. Earlier rubric drafts had a "Coverage of Allegations" criterion.
- **A time budget in the exercise:** a question limit or simulated clock (the app already has `MAX_QUESTIONS_PER_INTERVIEW` for online use), so that time spent on minor topics costs coverage of the important ones.
- **Widen Funneling's description** to include building toward the central issues, not just general-to-specific within a topic.
