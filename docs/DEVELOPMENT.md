# How Expert Interviewer was built

This document records how the prototype went from an idea to a working, published tool. It covers the process, every prompt used during the build, the feedback the coding assistant gave at each step, and what changed as a result.

## The process in brief

1. **Brainstorm and write a handoff doc with an AI assistant.** The idea was worked through in conversation with an AI assistant, which produced a structured technical handoff doc: agents, state, graph, endpoints, success criteria. GitHub Copilot was used here, but any capable AI assistant (ChatGPT, Claude, Gemini, Copilot, etc.) can do this step. The doc is preserved in [handoff-doc.md](handoff-doc.md).
2. **Hand the doc to an AI coding agent to build it.** The prototype was built with Claude Code (Claude, by Anthropic), working directly in the project folder. It wrote the code, ran it, tested it against the real model, and fixed what broke.
3. **Iterate with short, plain-language prompts.** Most changes came from one- or two-sentence requests. The agent proposed the next step at the end of each turn, and many prompts simply accepted that proposal.
4. **Publish.** The project was packaged with a setup guide and a worked example, then pushed to GitHub.

About 16 prompts took the project from an empty folder to a published repository.

## Timeline of prompts and feedback

Prompts are quoted exactly as typed. The feedback column summarizes what the assistant said and did in response.

### Phase 1: Building the prototype

**Prompt 1**
> I am going to provide you with a handoff doc from a tool I have been brainstorming. I want you to create a prototype.

*Feedback:* The doc wasn't attached yet. The assistant looked through the folder (it held only a LangChain quickstart file), asked for the doc, and asked two scoping questions: which tech stack, and command-line or web interface.

**Prompt 2**
> That file is removed. I want you to do whatever is fastest.

*Feedback:* The assistant took "fastest" as the guiding constraint and proposed a single-page web prototype with no build step. It still needed the doc itself.

**Prompt 3:** *(the handoff doc, pasted in full; see [handoff-doc.md](handoff-doc.md))*

*Feedback:* The assistant built the full MVP the doc described, scoped to its own advice to "deliver an MVP first with mocked storage and a single LLM provider":
- `InterviewState` and a LangGraph graph using the doc's node names. The interview loop pauses for user input and resumes on each message.
- Research, Criteria, Synthetic Expert, and Grader agents with structured (JSON) outputs.
- The five FastAPI endpoints, a config-driven persona file, and a one-page web UI.
- **Mock mode** with canned agent answers, so the whole flow could be demoed without an API key.
- In-memory storage plus JSON snapshots in place of PostgreSQL. Claude rather than Azure GPT-4o as the default model, switchable by one setting.

While testing, the first real-model call failed: the model rejected LangChain's default way of requesting structured output. The assistant switched to native JSON-schema output, reported that the fix was untested, and asked for an API key so it could verify.

### Phase 2: Testing with the real model

**Prompt 4**
> Key added, test it

followed mid-task by:

> The key is name Anthropic_API_KEY = [Key]

*Feedback:* The assistant confirmed the key was being picked up (Windows environment variable names aren't case-sensitive, so the capitalization was fine). The real run surfaced a second incompatibility: the model no longer accepts a `temperature` setting. The assistant removed it. The user paused the test before it re-ran.

**Prompt 5**
> Real quick how much will this run cost?

*Feedback:* About $0.10–$0.25 for the five-call test run, and roughly $0.40–$0.75 for a realistic 15-question interview. The assistant explained that most of the cost is output tokens, including the model's thinking, and that each turn resends the conversation so far. Cheaper options: lower "effort" settings, or a smaller model for the expert's replies.

**Prompt 6**
> Go for it.

*Feedback:* First full end-to-end run with the real model. Research, a tailored rubric, in-character answers, and calibrated grading all worked (a one-question interview correctly scored 10/F). The main weakness was a one-minute wait to start an interview. The assistant offered to speed it up.

### Phase 3: Performance

**Prompt 7**
> Yes, speed it up

*Feedback:* Setup went from 64 to 40 seconds and expert replies from 9 to 5 seconds. The changes:
- Per-agent effort levels (fast for setup, deeper for grading).
- Rubric generation and the greeting run in parallel.
- Shorter research output.

Measuring each step showed the real bottleneck was the model *writing* a long research package, not thinking, which is why the shorter output helped most. The assistant suggested starting the interview before the rubric was ready.

**Prompt 8**
> Yes, do it

*Feedback:* The rubric now builds in the background while the interview starts, and interviews open in about 27–30 seconds. The assistant noted this changes the step order in the handoff doc: the rubric is now finished during the interview instead of before it.

### Phase 4: Making it fit the real use case

**Prompt 9**
> A couple of things. First, the personas should be randomly determined and not revealed until the grade is released. Additionally, the criteria should not be determined by the user but by a criteria programed into the tool. I will provide a criteria in the future but for now I want you to take a stab at creating it.

*Feedback:*
- **Personas:** one is drawn at random per interview and hidden from every page and API response until grading. The assistant tested that nothing leaked. The expert is told never to name its own style, and the results page reveals it.
- **Rubric:** criteria now come from a fixed file (`rubric.json`) with weights and four scoring levels per criterion, editable without code changes. The assistant drafted 7 criteria, including a new "Adaptability to Expert Style" criterion that grades whether the interviewer noticed the hidden persona.
- **Two choices flagged for confirmation:** the Criteria Agent was kept, but limited to adding expert-specific "look-fors" for the grader, which stay hidden from the interviewer; and the user's stated objectives still counted toward one criterion.

**Prompt 10**
> Remove the interview objectives textbox from the webpage that is the purview of the criteria. Also worth noting is this is an expert interview of an expert within a company that is being investigated for a whistle blower complaint or a suspected white collar crime. Adjust the tool as would make sense.

*Feedback:* The biggest change of the project. The assistant reframed the tool from interviewing an academic expert to an **investigative witness interview**. It looked through the course folder and found an Enron events log (518 dated events with actors, quotes, and sources), which shaped the design.
- **Setup:** the objectives box is gone. New fields: witness name, role and company, case background, and an optional **case file** upload. Large files are trimmed to the rows that mention the witness.
- **Research** now produces an investigator's prep file: allegations, a dated timeline, relevant documents, red flags, and sensitive areas.
- **The witness** behaves like a real one: it answers only what is asked, gets more specific when shown documents, hedges in sensitive areas, and asks who the interviewer represents.
- **Personas** each gained a "witness posture", e.g. a guarded executive, or a founder who spins rule-bending as "moving fast".
- **The rubric** was rewritten for investigations: Upjohn warning and closing protocol, the open-to-closed questioning funnel, fact development, testing credibility with documents, coverage of allegations, and professionalism.
- **A problem found in testing and fixed:** the witness, played as Andrew Fastow, refused to continue without his own lawyer after the Upjohn warning, which ended the practice session. Since employees are usually expected to cooperate, the witness now raises the concern once and keeps answering.

### Phase 5: Test materials and publishing

**Prompt 11**
> Generate an example Background / outline to input in the web interface for an appropriate expert and a good amount of sample questions to ask for a manual test to receive a decent score.

*Feedback:* The assistant chose Andrew Fastow (Enron CFO) because the events log documents his inconsistencies best. It checked every fact against the log first, then wrote a 30-question script in six phases: opening, background, LJM1, Chewco/LJM2/Raptors, confronting the inconsistencies, and closing. It also explained which habits the rubric rewards and included a deliberately weak variant for comparison.

**Prompt 12**
> If you haven't already please create a document for setting this up off of a github repository. Also remind me how to publish it to my github. Next make this example a file in the folder so others can run through it.

*Feedback:* The assistant added:
- A setup guide (`SETUP.md`) for Windows and macOS.
- A `.gitignore` that keeps the API key and session transcripts out of the repository, plus minimum package versions.
- The example as a self-contained folder (`examples/enron-fastow/`) with its own copy of the case file.

It tested a fresh copy in mock mode, confirmed exactly which files git would commit, and gave the step-by-step GitHub publishing commands.

**Prompts 13–16**
> Yes, push it

> Created it

> Here's the URL

> This is the URL: https://github.com/haycon0/expert-interviewer.git. Finally can you make a summary document of how we developed this tool including the prompts that I used and a summary of the feedback you gave to those prompts. FYI I used copilot to generate the handoff doc but make sure to say any AI could be used.

*Feedback:* The GitHub CLI wasn't installed, so the assistant committed locally (checking again that the API key file was excluded) and asked for the empty repository to be created on GitHub. It found the GitHub account saved on the computer, but couldn't see the new repo until it had the exact URL. It then pushed the project and wrote this document.

## How the tool ended up differing from the handoff doc

| Handoff doc | Final prototype | Why |
|---|---|---|
| User selects a persona | Persona is random and hidden until grading | Prompt 9: grading should test whether the interviewer adapts |
| Criteria Agent creates a custom rubric from user objectives | Fixed rubric in `rubric.json`; the agent only adds case-specific look-fors | Prompt 9: criteria belong to the tool, not the user |
| User enters interview objectives | Removed; replaced by case background and a case file | Prompt 10 |
| General expert interview | Investigative interview of an employee witness | Prompt 10 |
| Rubric generated before the interview | Rubric built in the background during the interview | Prompt 8: faster start |
| Azure OpenAI GPT-4o | Claude by default; Azure is a one-line setting change | Fastest path (Prompt 2) |
| PostgreSQL / Redis | In-memory storage plus JSON snapshots | The doc itself said to start with mocked storage |

## Lessons from the process

- **A structured handoff doc made the first build fast.** Because the doc named the agents, state fields, graph nodes, and endpoints, the first working version came from a single prompt.
- **Short prompts work when the assistant proposes the next step.** "Yes, speed it up" and "Yes, do it" were enough because each turn ended with a concrete, specific suggestion.
- **Testing against the real model mattered.** Two incompatibilities and the "witness refuses to continue" problem only showed up in real runs.
- **The biggest improvement came from telling the assistant the actual use case.** Explaining that this was a whistleblower or white-collar investigation changed the research, the witness, the personas, and the rubric far more than any technical change.
- **Ask about cost before running.** A quick estimate kept testing cheap and predictable.
