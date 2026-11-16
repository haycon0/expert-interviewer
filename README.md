# Expert Interviewer

**Practice investigative interviews with an AI witness, then get graded and coached.**

You play an investigator looking into a whistleblower complaint or suspected white-collar crime. You interview an employee of the company, played by AI. The tool:

1. **Checks your case documents** (PDF, Word, or text). Anything that looks added by mistake is flagged, such as an email meant for someone else or a file from a different case. You see what it contains and decide whether to keep it.
2. **Plays the witness** in a live chat. The witness knows only your case background and the documents you kept, and has a personality chosen at random and kept secret. Some witnesses are cooperative, some guarded, some evasive.
3. **Grades your interview** against a fixed rubric: 23 skills in four areas (framing and closing, question technique, fact development and credibility testing, and document use), each rated 0 to 4 with the moments in the interview that back it up. Then it gives you tips and reveals the witness's personality.

It runs on your own computer, in your web browser. An interview costs roughly $0.40–$0.75 in AI usage, and there's a free demo mode for trying it out.

## Get started

**New to this? Start here → [SETUP.md](SETUP.md).** It walks you through everything step by step, with no coding experience needed. Once it's set up, you start the app by double-clicking a file.

## Try the practice interview

[`examples/enron-fastow`](examples/enron-fastow/README.md) is a ready-made practice run: you interview Andrew Fastow, Enron's former CFO. It tells you exactly what to enter and gives you 30 questions to ask.

## How it works

[docs/HOW-IT-WORKS.md](docs/HOW-IT-WORKS.md) explains what happens behind the scenes: the four AI agents and what each one sees, how the witness behaves, how grading and scoring work, what stays hidden until the end, where your information goes, and what each step costs. It's written in plain language first, with technical details for developers at the end.

## Cheaper models and other AI providers

Choose the AI engine on the setup page for each interview. The list runs from high-powered models (Claude Opus and Fable, GPT-6 Astra, Gemini 4 Argon) to cost-effective ones (Claude Haiku 5.5, GPT-6 Luna, Gemini Flash-Lite, DeepSeek Flash) and free models that run on your own computer through Ollama. If a model isn't set up, the page tells you exactly what to do. [docs/MODELS.md](docs/MODELS.md) covers the options, costs, and setup for each company.

## Voice and face

Interview by **text**, by **voice** (talk to the witness and hear it answer), or by **voice with a face** that reacts with the witness's mood. Free options use your browser's built-in voice and an animated face. Paid options include OpenAI, ElevenLabs, and Deepgram voices, and lifelike faces from Simli, D-ID, Tavus, and HeyGen. See [docs/VOICE-AND-FACE.md](docs/VOICE-AND-FACE.md).

## Publishing it online

This is the **full version**, for running on your own computer with every model, voice, and face option.

A separate **online version** lives on the [`online` branch](https://github.com/haycon0/expert-interviewer/tree/online). It's the copy that can be put on the internet behind a shared password, and it offers only the lower-cost options (Claude Haiku, the free browser voice, and the free animated face). Its publishing guide is in `docs/PUBLISHING.md` on that branch.

## Debugging

For testing, click **Debug page** on the setup page (or go to `/debug`): it fills in the Enron example for you. [docs/DEBUGGING.md](docs/DEBUGGING.md) explains it: choose the witness's persona and variations, start from a scripted interview that's halfway through or one question from the end, and skip the document check.

## How interviews are graded

[docs/ASSESSMENT.md](docs/ASSESSMENT.md) summarizes how the tool assesses an interview: what the grader reads, the 23 skills and their marks, how the score is calculated, the score caps, and the limitations. [docs/INTERVIEW-OUTLINE.md](docs/INTERVIEW-OUTLINE.md) is a template outline for planning an interview, including the Upjohn warning.

## How this was built

[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) tells how the tool was built entirely with AI tools and plain-English requests, starting from an AI-written plan ([docs/handoff-doc.md](docs/handoff-doc.md)). It includes every prompt used, what the AI did in response, and how to do the same yourself.

---

## For developers

A LangGraph multi-agent app (Document Checker → human review → Synthetic Expert (multi-turn) → Grader) with a FastAPI backend and a single-page UI.

- Uploaded documents (.pdf, .docx, .txt, .csv, .md, .json) are checked for relevance in parallel. If any are flagged, the graph pauses (`interrupt`) for the user to keep or remove each one.
- The witness and grader agents read only the case background and the kept documents. There's no research step and no outside knowledge. Large sets are trimmed to about 60K characters, preferring passages that mention the witness.
- The witness persona is drawn at random and revealed only with the grade.
- Grading uses a fixed rubric (`rubrics/v2.2.json`). The grader only rates each skill 0–4 and cites turn numbers; `grading_v2.py` computes the marks, caps and band. The previous rubric (`rubric.json`, with the Criteria agent's case-specific look-fors) can be chosen on the debug page for comparison.

```
pip install -r requirements.txt
copy .env.example .env      # then add your API key
python -m uvicorn server:app --reload
```

| File | What it is |
|---|---|
| `start.bat` / `start.command` | Double-click launchers (Windows / Mac): first-time setup, API key prompt, start server, open browser. |
| `graph.py` | `InterviewState` + LangGraph orchestration. The interview loop pauses with `interrupt()` and resumes on each API call. |
| `agents.py` | Document Checker, Criteria, Synthetic Expert, and Grader agents (structured outputs via Pydantic); per-agent `EFFORT` settings; prompt caching. |
| `documents.py` | Text extraction from uploads, and combining kept documents into the agents' case file. |
| `server.py` | FastAPI endpoints + UI route. |
| `personas.json` | Persona library (style traits + witness posture + a personality-specific variation). |
| `variables.json` | Random variations added to most interviews (communication style, candor, etc.) and how often they appear. |
| `rubrics/v2.2.json` | The grading rubric: areas, skills and marks, the 0–4 scale, score caps, result bands, and the interview-outline reference. |
| `grading_v2.py` | Grading with the rubric: the grader's prompt and output schema, and the scoring (marks, caps, band) in code. |
| `rubric.json` | The previous rubric (draft 2), kept for comparison on the debug page. |
| `static/index.html` | Single-page UI: setup → interview → results. |
| `examples/` | Worked practice interviews with case files. |
| `models.json`, `model_catalog.py` | The model list for the setup page, and setup-status checks. |

**Model:** set `MODEL` in `.env` to any LangChain `init_chat_model` string (default `anthropic:claude-sonnet-5-5`). Override individual agents with `MODEL_WITNESS`, `MODEL_CHECKER`, `MODEL_CRITERIA`, or `MODEL_GRADER`. OpenAI, Azure OpenAI, Google Gemini, and Ollama packages are installed; more providers are commented out in `requirements.txt`. See [docs/MODELS.md](docs/MODELS.md).

**Not yet built (from the handoff doc):** PostgreSQL/Redis persistence (sessions are in memory plus JSON files, so they're lost on restart), web research and citations, Azure services, Dataverse, voice, multi-expert panels.
