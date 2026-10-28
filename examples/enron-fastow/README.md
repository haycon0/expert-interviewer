# Manual test script: Andrew Fastow (Enron)

Facts below are taken from [`Enron_Sample_Events_Log.csv`](Enron_Sample_Events_Log.csv) in this folder, mostly the Powers Report entries (source S077) and the June 28, 1999 board materials (S003).

## 1. Setup fields

**Witness name**
```
Andrew Fastow
```

**Role and company**
```
Executive Vice President and CFO, Enron Corp.
```

**Case background** (also in [`case_background.txt`](case_background.txt) for easy copying)
```
It is November 2001. Enron's Board has formed a Special Investigative Committee after an employee's internal memo warned that the company could "implode in a wave of accounting scandals," and after Enron announced a $1.2 billion reduction in shareholders' equity tied to the LJM partnerships. Enron has also said it will restate its 1997-2001 financial statements because of accounting errors involving LJM1 and Chewco.

The Committee is investigating transactions between Enron and partnerships run by Enron's CFO, Andrew Fastow, and his subordinate Michael Kopper: Chewco (1997), LJM1 and the Rhythms NetConnections hedge (1999-2000), LJM2, and the Raptor hedging vehicles (2000-2001). Key questions: whether the Board was given accurate information when it waived the Code of Conduct to let Fastow run LJM; whether Fastow or other employees received undisclosed payments from these partnerships; whether the partnerships let Enron hide losses and keep debt off its balance sheet; and whether the controls the Board relied on (review by Causey and Buy, Audit Committee review) actually worked.

The interviewer is outside counsel retained by the Special Committee.
```

**Case file:** click "Choose file" and pick `examples/enron-fastow/Enron_Sample_Events_Log.csv`.

## 2. How to score well

The rubric rewards *how* you ask as much as *what* you ask:

- **One question per message.** Compound questions cost points.
- **Start with open questions, then narrow down.** Begin with "walk me through...", then pin down names, dates and amounts.
- **Follow up on every vague answer** ("I don't recall", "that was normal", "the Board approved it") before moving on. The scripted questions below are a backbone. Your follow-ups are what score.
- **Ask how he knows things.** Separate what he saw himself from what he heard from someone else.
- **Hold your documents until Part E.** Let him commit to his version first, then confront him calmly and give him a chance to explain.
- **Adapt to his demeanor.** It's random. If he is terse, ask shorter, more specific questions. If he spins, ask for specifics. If he's talkative, steer.
- **Close properly** (Part F).

Expect 20-30 messages in total, counting follow-ups. Placeholders in [brackets] mean "fill in from what he just said."

## 3. Questions

### A. Opening (send as one message)
1. Good morning, Mr. Fastow. My name is [name]. I'm outside counsel retained by the Special Investigative Committee of Enron's Board. I represent the Committee and the company, not you personally. This conversation is privileged, but the privilege belongs to the company, and the company may decide to waive it and share what you tell me with others, including the government. Please keep the contents of this interview confidential. Enron does not tolerate retaliation against anyone for cooperating. Do you have any questions before we begin?

> If he asks about his own lawyer, answer briefly and neutrally: "You're free to consult your own counsel. Today I'd like to hear your understanding of these transactions." Then go to question 2.

### B. Background (open, rapport)
2. To start, could you describe your role as CFO and what the Global Finance group was responsible for?
3. Who reported to you in Global Finance during 1999 and 2000?
4. What was Michael Kopper's role in your group?

### C. LJM1 and the Rhythms hedge (open first, then narrow)
5. Walk me through how the idea for LJM1 came about in 1999.
6. What problem was the Rhythms NetConnections hedge meant to solve?
7. Why did you need to be the general partner, as opposed to someone outside Enron?
8. What did you tell Mr. Lay and Mr. Skilling about your role before it went to the Board?
9. Tell me about the June 28, 1999 Board meeting. What did you present?
10. What did you tell the Board about how you personally would be compensated by LJM?

> Lock it in: "So your understanding at the time was that you would not benefit from the value of Enron stock held by LJM. Is that right?" Then move on without revealing anything.

11. How was the Rhythms hedge unwound in early 2000?
12. Who negotiated the unwind on Enron's side, and who on LJM's side?

### D. Chewco, LJM2, and the Raptors
13. How did Chewco come to be formed in 1997?
14. Why was Michael Kopper chosen to manage Chewco instead of you?
15. Who at Enron knew that Kopper was involved in Chewco? *(Follow up: how do you know that?)*
16. What role did you play in the 2001 buyout of Chewco's interest in JEDI?
17. What controls were put in place when the Board approved LJM2 in October 1999?
18. How did those controls work in practice? Who actually reviewed each deal? *(Ask for a specific example.)*
19. What return did you tell the Finance Committee LJM2 would earn on the Raptor transactions?
20. What returns did LJM2 actually earn on the Raptors?

### E. Testing inconsistencies (only after he has committed above)
21. I'd like to show you the Southampton Place partnership agreement, dated March 20, 2000. It lists a $25,000 contribution from the Fastow Family Foundation. What was Southampton Place?
22. Our information is that about two months later the Foundation received roughly $4.5 million on that $25,000. How does that square with what you told the Board in June 1999 about not receiving any value from Enron stock?
23. Who else at Enron invested in Southampton Place? *(Follow up: who invited them?)*
24. Earlier you said [his answer to Q16]. We have a handwritten memo addressed to "Andy" that references $10.5 million for the Chewco buyout. Can you explain that memo?
25. In October 2000 you reported LJM2 returns of 193%, 278%, and 2,500% on Raptor deals, compared with the roughly 30% presented to the Board. Why weren't those returns disclosed to the Board?
26. In September 2001, in-house counsel advised that Enron had no obligation to make a $2.6 million tax indemnity payment to Chewco. Did you authorize that payment anyway?

### F. Closing
27. Is there anything I haven't asked about that you think the Committee should know?
28. Who else should we speak with to understand these transactions?
29. What documents should we look at, and do you have any personal files, notes, or emails related to LJM, Chewco, or Southampton?
30. Please keep any such documents, including personal emails and files, and don't delete or discard anything. Also, please don't discuss today's interview with anyone else at the company. Is there anything you'd like to add or correct before we finish?

## 4. What to expect

- **Opening:** if you deliver Part A as written, he will likely ask about counsel, then cooperate.
- **Score:** following the script with real follow-ups on his vague answers should land in the B range or better. The biggest swings come from Fact Development & Follow-Up and Testing Credibility (35% of the grade together).
- **Missed opportunities:** the grade report lists what you didn't get to, so you can rerun and compare.
- **Testing the grader:** for a low-score baseline, ask only questions 5, 9, and 13 with no opening, follow-ups, or close.
