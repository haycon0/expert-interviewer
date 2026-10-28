# How Expert Interviewer was built

This is the story of how Expert Interviewer went from an idea to a working tool shared on GitHub. **No coding was done by hand.** Every step was a plain-English request to AI tools. The document lists every request (called a "prompt") that was typed, what the AI said and did in response, and what you can learn from it.

You don't need any technical background to follow it. Terms are explained as they come up, and there's a glossary at the end.

---

## The short version

1. **Brainstorm with an AI chat assistant.** The idea was talked through with an AI assistant, which then wrote a "handoff doc": a detailed plan describing what the tool should do and how its parts fit together. GitHub Copilot was used here, but **any AI chat assistant can do this step** (ChatGPT, Claude, Gemini, Copilot, and so on). The plan is saved in [handoff-doc.md](handoff-doc.md).
2. **Give the plan to an AI coding assistant.** The plan was pasted into Claude Code, an app from Anthropic in which the Claude AI can create files, write the program, run it, and test it on your computer. It built the first working version from that one message.
3. **Improve it with short requests.** Over about 17 messages, most of them one or two sentences, the tool was tested, sped up, and reshaped for its real purpose: practicing interviews in corporate investigations.
4. **Share it.** The AI packaged the project with instructions and an example, then published it to GitHub so others can download it.

---

## What the tool does

Expert Interviewer is a practice tool. You play an investigator interviewing an employee (the "witness") at a company under investigation for a whistleblower complaint or suspected white-collar crime. Behind the scenes, several AI "agents" (separate AI helpers, each with one job) work together:

- **Research agent:** builds a file on the witness: role, timeline, documents, red flags.
- **Witness agent:** plays the witness in a live conversation, with a personality chosen at random and kept hidden.
- **Criteria agent:** adds case-specific notes to a fixed grading rubric.
- **Grader agent:** scores your interview when you finish and coaches you.

---

## Every prompt, and what happened

Prompts are quoted exactly as typed, typos included. Under each is a plain-language summary of the AI's response.

### Part 1: Getting a first version

**Prompt 1**
> I am going to provide you with a handoff doc from a tool I have been brainstorming. I want you to create a prototype.

**What happened:** The plan hadn't been pasted yet. The AI looked in the project folder, found only an unrelated sample file, and asked for the plan. It also asked two questions: what technology to use, and whether the tool should run in a web page or a text window.

**Prompt 2**
> That file is removed. I want you to do whatever is fastest.

**What happened:** The AI took "fastest" as its guiding rule and chose a simple web page that runs on your own computer.

**Prompt 3:** *(the handoff doc, pasted in full; see [handoff-doc.md](handoff-doc.md))*

**What happened:** From this one message, the AI built a complete working first version:
- The four agents, plus a "conductor" that runs them in order and remembers the conversation. The plan called for a tool named LangGraph for this.
- A web page with three screens: set up the interview, chat with the expert, and see your grade.
- A **demo mode** with pre-written answers, so the tool could be tried before connecting it to a real AI model.
- Simple stand-ins for the database and cloud services the plan mentioned, as the plan itself suggested for a first version.

When the AI tried a real AI model for the first time, it hit an error: the model rejected the way the request was formatted. The AI fixed it, said the fix still needed testing, and asked for an API key (the password that lets the program use the AI model) so it could check.

### Part 2: Testing with the real AI model

**Prompt 4**
> Key added, test it

sent with a follow-up while the AI was working:

> The key is name Anthropic_API_KEY = [Key]

**What happened:** The AI confirmed the key was being read correctly; the capitalization didn't matter. Testing turned up a second compatibility problem (an outdated setting the model no longer accepts), which the AI removed. The test was paused before it ran again.

**Prompt 5**
> Real quick how much will this run cost?

**What happened:** The AI looked up current prices and estimated about **$0.10–$0.25** for the test, and about **$0.40–$0.75** for a realistic 15-question interview. It explained that cost depends on how much text the AI writes, including its behind-the-scenes "thinking", and that longer interviews cost more per question because the whole conversation is re-sent each time. It also suggested ways to make it cheaper.

**Prompt 6**
> Go for it.

**What happened:** The first complete run with the real AI worked. It researched the expert, built a rubric, held an in-character conversation, and graded the interview. A one-question interview correctly got an F. The main problem was a **one-minute wait** before each interview started, and the AI offered to fix it.

### Part 3: Making it faster

**Prompt 7**
> Yes, speed it up

**What happened:** The wait dropped from 64 to 40 seconds, and the expert's replies from 9 to 5 seconds. The AI:
- Told each agent how hard to "think" (quick for setup, careful for grading).
- Had two steps run at the same time instead of one after the other.
- Asked the research agent for a shorter write-up.

It measured each step and found the biggest delay was the research agent *writing* a long report, so the shorter report helped most.

**Prompt 8**
> Yes, do it

**What happened:** The grading rubric is now built quietly in the background while the interview starts, cutting the wait to about **27–30 seconds**. The AI pointed out that this changed the order of steps from the original plan.

### Part 4: Shaping it for its real purpose

**Prompt 9**
> A couple of things. First, the personas should be randomly determined and not revealed until the grade is released. Additionally, the criteria should not be determined by the user but by a criteria programed into the tool. I will provide a criteria in the future but for now I want you to take a stab at creating it.

**What happened:**
- **Hidden personalities:** the expert's personality (e.g. "Executive Leader" or "Friendly Mentor") is now picked at random and kept secret until the grade appears. The AI checked that it couldn't leak early anywhere.
- **A fixed rubric:** grading now uses a set list of criteria stored in one easy-to-edit file (`rubric.json`) instead of being invented for each interview. The AI drafted 7 criteria with four score levels each, including one that rewards noticing and adapting to the hidden personality.
- **Two judgment calls flagged for approval:** the criteria agent stays, but only to add notes specific to the expert, which are hidden from the interviewer; and the interviewer's stated goals still counted toward one criterion.

**Prompt 10**
> Remove the interview objectives textbox from the webpage that is the purview of the criteria. Also worth noting is this is an expert interview of an expert within a company that is being investigated for a whistle blower complaint or a suspected white collar crime. Adjust the tool as would make sense.

**What happened:** This was the biggest change. Up to now the tool interviewed academic experts. The AI rebuilt it around **investigation interviews**. It also found a course file listing 518 dated Enron events, and used it to shape the design.
- **Setup page:** the goals box is gone. New boxes: witness name, role, case background, and an optional **case file** upload. Big files are automatically trimmed to the parts that mention the witness.
- **Research:** produces an investigator's prep file: allegations, a dated timeline, key documents, red flags, and topics where the witness is likely to be evasive.
- **The witness** acts like a real one: it answers only what's asked, gets more specific when shown documents, hedges on sensitive topics, and may ask who the interviewer represents.
- **Personalities** each got a matching witness style, e.g. a guarded executive, or a founder who brushes off rule-breaking as "moving fast".
- **The rubric** was rewritten around investigative interviewing:
  - a proper opening, including the standard explanation of whom the interviewer represents (an "Upjohn warning"), and a proper close
  - starting with open questions and narrowing down
  - pinning down facts
  - testing the witness's story against documents
  - covering the allegations
  - professionalism
- **A problem found in testing and fixed:** the AI-played witness (Andrew Fastow, Enron's CFO) refused to say anything without his own lawyer, which ended the practice session immediately. Employees are usually expected to cooperate with company investigations, so the witness now raises the concern once and then keeps answering.

### Part 5: Practice materials and sharing

**Prompt 11**
> Generate an example Background / outline to input in the web interface for an appropriate expert and a good amount of sample questions to ask for a manual test to receive a decent score.

**What happened:** The AI chose Andrew Fastow because the Enron records document his contradictions best. It checked every fact against those records, then wrote a 30-question practice script in six stages: opening, background, the first partnership, the later deals, confronting contradictions, and closing. It explained what the grader rewards, and added a deliberately weak version for comparison.

**Prompt 12**
> If you haven't already please create a document for setting this up off of a github repository. Also remind me how to publish it to my github. Next make this example a file in the folder so others can run through it.

**What happened:** The AI wrote setup instructions, made sure the private API key file can never be uploaded by accident, and turned the practice script into its own folder with everything needed to run it. It tested a fresh copy and gave step-by-step publishing instructions.

**Prompts 13–16**
> Yes, push it

> Created it

> Here's the URL

> This is the URL: https://github.com/haycon0/expert-interviewer.git. Finally can you make a summary document of how we developed this tool including the prompts that I used and a summary of the feedback you gave to those prompts. FYI I used copilot to generate the handoff doc but make sure to say any AI could be used.

**What happened:** A GitHub helper program the AI would normally use wasn't installed, so the AI prepared everything and asked for an empty project to be created on the GitHub website first. Once it had the exact web address, it uploaded ("pushed") the project and wrote this document.

**Prompt 17**
> Assume that the person has absolutely no familiarity with code, IDEs, or claude code. I want the setup and development docs to be accessible to even them.

**What happened:** The AI rewrote the setup guide and this document in plain language. It also added **double-click start files** for Windows and Mac, so nobody has to type commands. They install what's needed the first time, ask for the API key, and open the app in the browser. While testing them as a brand-new user would, the AI found and fixed a bug where the start file could miss the pasted key.

---

## How the final tool differs from the original plan

| Original plan | Final tool | Why |
|---|---|---|
| User picks the expert's personality | Personality is random and secret until grading | Grading should test whether you notice and adapt (Prompt 9) |
| Grading criteria invented per interview from the user's goals | One fixed rubric; the AI only adds case-specific notes | Criteria belong to the tool, not the user (Prompt 9) |
| User types interview goals | Removed; replaced by case background and an evidence file | Prompt 10 |
| Any kind of expert interview | Investigation interview of an employee witness | Prompt 10 |
| Rubric built before the interview starts | Built in the background during the interview | Faster start (Prompt 8) |
| Microsoft's Azure AI service | Anthropic's Claude, switchable with one setting | "Whatever is fastest" (Prompt 2) |
| Full database | Simple temporary storage | The plan itself said to start simple |

---

## Do it yourself: building a tool this way

You can follow the same process with no coding experience:

1. **Brainstorm with any AI chat assistant.** Describe your idea and who it's for. When it's clear, ask: *"Write a technical handoff doc for an AI coding assistant to build a prototype of this."*
2. **Open an AI coding assistant in an empty folder.** This project used the Claude Code desktop app; similar tools exist. Paste the handoff doc and say *"Create a prototype."* Add *"do whatever is fastest"* if you don't have technical preferences.
3. **Test with a real AI model, and ask about cost first.** A quick *"how much will this cost?"* keeps things predictable.
4. **Tell it who the tool is really for.** The single most useful message in this project was explaining the actual use case (investigations), not any technical request.
5. **Accept or redirect its suggestions.** The AI ends most replies by proposing a next step. "Yes, do it" is a perfectly good prompt.
6. **Ask for instructions others can follow, then ask it to publish.** It can write setup guides and upload the project for you.

## Lessons learned

- **A detailed plan up front made the first version fast.** One message produced a working tool, because the plan named every piece.
- **Short prompts work** when the AI proposes the next step clearly.
- **Real testing finds real problems.** Three issues (two compatibility errors and the witness who wouldn't talk) only appeared when the tool was tried for real.
- **Context beats technique.** Explaining the real-world purpose improved the tool more than anything else.

---

## Glossary

| Term | Meaning |
|---|---|
| **Agent** | An AI helper with one specific job, like researching or grading. |
| **AI coding assistant** | An app where an AI writes, runs, and fixes a program for you based on plain-English requests. Claude Code is one. |
| **API key** | A private password that lets a program use an AI model. It's also how the AI company bills you. |
| **Demo mode / mock mode** | Running the tool with pre-written answers instead of a real AI model. Free, for trying it out. |
| **GitHub** | A website for storing and sharing projects. |
| **Handoff doc** | A written plan describing what to build, meant to be handed to whoever (or whatever AI) builds it. |
| **Persona** | The personality the AI witness is given (e.g. guarded executive, friendly mentor). |
| **Prompt** | A message you type to an AI. |
| **Prototype** | An early working version, built to try an idea, not a finished product. |
| **Push** | Uploading your latest changes to GitHub. |
| **Repository (repo)** | One project's folder on GitHub. |
| **Rubric** | The scoring guide: what's graded, how much each part counts, and what good looks like. |
| **Upjohn warning** | The explanation a company's lawyer gives an employee at the start of an interview: the lawyer represents the company, not the employee, and the company controls what's done with the conversation. |
