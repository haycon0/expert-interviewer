# Expert Interviewer

**Practice investigative interviews with an AI witness, then get graded and coached.**

You play an investigator looking into a whistleblower complaint or suspected white-collar crime. You interview an employee of the company, played by AI. The tool:

1. **Researches the witness** and gives you a prep file: their role, a timeline, key documents, and red flags.
2. **Plays the witness** in a live chat, with a personality chosen at random and kept secret. Some witnesses are cooperative, some guarded, some evasive.
3. **Grades your interview** against a fixed rubric: your opening, questioning technique, follow-up, testing the witness's story, coverage, and professionalism. Then it coaches you and reveals the witness's personality.

It runs on your own computer, in your web browser. An interview costs roughly $0.40–$0.75 in AI usage, and there's a free demo mode for trying it out.

## Get started

**New to this? Start here → [SETUP.md](SETUP.md).** It walks you through everything step by step, with no coding experience needed. Once it's set up, you start the app by double-clicking a file.

## Try the practice interview

[`examples/enron-fastow`](examples/enron-fastow/README.md) is a ready-made practice run: you interview Andrew Fastow, Enron's former CFO. It tells you exactly what to enter and gives you 30 questions to ask.

## How it works

[docs/HOW-IT-WORKS.md](docs/HOW-IT-WORKS.md) explains what happens behind the scenes: the four AI agents and what each one sees, how the witness behaves, how grading and scoring work, what stays hidden until the end, where your information goes, and what each step costs. It's written in plain language first, with technical details for developers at the end.

## How this was built

[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) tells how the tool was built entirely with AI tools and plain-English requests, starting from an AI-written plan ([docs/handoff-doc.md](docs/handoff-doc.md)). It includes every prompt used, what the AI did in response, and how to do the same yourself.

---

## For developers

A LangGraph multi-agent app (Research → Synthetic Expert (multi-turn) → Criteria → Grader) with a FastAPI backend and a single-page UI.

- The witness persona is drawn at random and revealed only with the grade.
- Grading uses a fixed rubric (`rubric.json`). The Criteria Agent only adds case-specific "look-fors" under each criterion.
- An optional case file (.txt/.csv/.md/.json) feeds the Research Agent; large files are trimmed to rows mentioning the witness.

```
pip install -r requirements.txt
copy .env.example .env      # then add your API key
python -m uvicorn server:app --reload
```

| File | What it is |
|---|---|
| `start.bat` / `start.command` | Double-click launchers (Windows / Mac): first-time setup, API key prompt, start server, open browser. |
| `graph.py` | `InterviewState` + LangGraph orchestration. The interview loop pauses with `interrupt()` and resumes on each API call. |
| `agents.py` | Research, Criteria, Synthetic Expert, and Grader agents (structured outputs via Pydantic); per-agent `EFFORT` settings. |
| `server.py` | FastAPI endpoints + UI route. |
| `personas.json` | Persona library (style traits + witness posture). |
| `rubric.json` | Grading rubric: criteria, weights, level descriptions. |
| `static/index.html` | Single-page UI: setup → interview → results. |
| `examples/` | Worked practice interviews with case files. |
| `sessions/` | JSON snapshot of each session. Not committed to git. |

**Model:** set `MODEL` in `.env` to any LangChain `init_chat_model` string, e.g. `anthropic:claude-sonnet-5-5` (default) or `azure_openai:gpt-4o` (also set `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `OPENAI_API_VERSION`, and `pip install langchain-openai`).

**Not yet built (from the handoff doc):** PostgreSQL/Redis persistence (sessions are in memory plus JSON files, so they're lost on restart), web research and citations, Azure services, Dataverse, voice, multi-expert panels.
