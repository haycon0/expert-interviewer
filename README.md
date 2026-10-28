# Expert Interviewer (MVP prototype)

Multi-agent interview simulator for investigations: practice interviewing an expert employee inside a company under investigation for a whistleblower complaint or suspected white-collar misconduct. Research Agent → Synthetic Expert (the witness, multi-turn) → Criteria Agent → Grader, orchestrated with LangGraph.

- The witness's demeanor (persona) is drawn at random and revealed only with the grade.
- Grading uses a fixed, tool-defined rubric (`rubric.json`), not user input. The Criteria Agent only adds case-specific "look-fors" under each fixed criterion.
- An optional case file (.txt/.csv/.md/.json, e.g. an events log) feeds the Research Agent; large files are trimmed to the rows that mention the witness.

## Quick start

Full step-by-step instructions (Windows and macOS) are in **[SETUP.md](SETUP.md)**.

```
pip install -r requirements.txt
copy .env.example .env      # then add your API key
python -m uvicorn server:app --reload
```

Open http://127.0.0.1:8000. With no API key it runs in **mock mode** (canned agent output) so you can click through the flow.

## Try the example

[`examples/enron-fastow/`](examples/enron-fastow/README.md) is a practice interview with Enron's CFO, Andrew Fastow: setup fields, a case file to upload, and a 30-question script that should score well.

## How it was built

[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) walks through the build, from an AI-generated handoff doc ([docs/handoff-doc.md](docs/handoff-doc.md)) to the published tool, with every prompt used and the feedback given at each step.

## Files

| File | What it is |
|---|---|
| `graph.py` | `InterviewState` + LangGraph (Master Agent orchestration). The interview loop pauses with `interrupt()` and resumes on each API call. |
| `agents.py` | Research, Criteria Creator, Synthetic Expert, Grader agents (structured outputs via Pydantic). |
| `server.py` | FastAPI endpoints from the handoff doc + UI route. |
| `personas.json` | Persona library (style traits + witness posture) — add entries here, no code changes needed. |
| `rubric.json` | The grading rubric: criteria, weights, and level descriptions. Edit to change grading. |
| `static/index.html` | Single-page UI: setup → interview → results. |
| `examples/` | Worked practice interviews with case files. |
| `sessions/` | JSON snapshot of each session (metadata, research, rubric, transcript, assessment). Not committed to git. |

## LLM provider

Set `MODEL` in `.env` to any `init_chat_model` string, e.g. `anthropic:claude-sonnet-5-5` (default) or `azure_openai:gpt-4o` (also set `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `OPENAI_API_VERSION`, and install `langchain-openai`).

## Not yet built (per handoff doc)

PostgreSQL/Redis persistence (currently in-memory `MemorySaver` + JSON files, so sessions are lost on server restart), web research tools/citations, Azure services, Dataverse, voice, multi-expert panels.
