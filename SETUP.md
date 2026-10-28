# Setting up Expert Interviewer from GitHub

This takes about 5 minutes. You need:

- **Python 3.11 or newer.** Check with `python --version`. Get it from [python.org](https://www.python.org/downloads/). On Windows, tick "Add python.exe to PATH" in the installer.
- **Git.** Check with `git --version`. Get it from [git-scm.com](https://git-scm.com/downloads). You can also download the repo as a ZIP from GitHub (green **Code** button → **Download ZIP**) and skip step 1.
- **An Anthropic API key**, from [console.anthropic.com](https://console.anthropic.com/). Without one, the app still runs in **mock mode** with canned answers, which is useful for checking the install.

## 1. Get the code

```
git clone https://github.com/<owner>/expert-interviewer.git
cd expert-interviewer
```

Replace `<owner>/expert-interviewer` with the repository's actual path.

## 2. Create a virtual environment and install packages

**Windows (PowerShell)**
```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
If PowerShell says running scripts is disabled, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, then activate again.

**macOS / Linux**
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Add your API key

Copy the example settings file:

- Windows: `copy .env.example .env`
- macOS / Linux: `cp .env.example .env`

Open `.env` in a text editor and paste your key after `ANTHROPIC_API_KEY=`, with no quotes or spaces:

```
ANTHROPIC_API_KEY=sk-ant-...
MODEL=anthropic:claude-sonnet-5-5
```

`.env` is listed in `.gitignore`, so your key is never committed. Never put the key in any other file.

## 4. Run it

```
python -m uvicorn server:app --reload
```

Open http://127.0.0.1:8000. The top-right corner shows the model in use, or **Mock mode (no API key)** if it can't find your key.

Stop the server with `Ctrl+C`. Next time, just activate the virtual environment (step 2's activate line) and run step 4.

## 5. Try the worked example

[`examples/enron-fastow/`](examples/enron-fastow/README.md) is a complete practice interview with Enron's former CFO, Andrew Fastow. It has the setup fields to enter, a case file to upload, and 30 questions designed to score well.

## Cost

With the default model (Claude Sonnet 5.5), a typical 15-25 question interview costs roughly $0.40-$0.75 in API usage. Starting an interview (research) takes about 30 seconds.

## Troubleshooting

| Problem | Fix |
|---|---|
| Badge says **Mock mode** even though you added a key | Check the file is named exactly `.env` (not `.env.txt`; Windows may hide the extension), is in the project folder, and the key has no quotes or spaces. Restart the server. |
| `python` not found | Reinstall Python with "Add to PATH" ticked, or try `py` (Windows) or `python3` (macOS). |
| `Address already in use` | Another server is on port 8000. Stop it, or run with `--port 8001` and open http://127.0.0.1:8001. |
| `UserWarning: Core Pydantic V1 functionality...` | Harmless on Python 3.14. Ignore it. |
| Error starting an interview: `400 ... invalid_request_error` | Your account may not have access to the model in `MODEL`. Set it to another model your key can use. |
| Sessions disappear after a restart | Expected for this prototype: sessions are kept in memory. JSON copies are saved in `sessions/`. |

## Customizing

- **Grading criteria:** edit [`rubric.json`](rubric.json): criteria, weights (must total 100), and level descriptions.
- **Witness demeanors:** edit [`personas.json`](personas.json). One is drawn at random per interview.
- **Speed and cost per agent:** change the `EFFORT` table in [`agents.py`](agents.py).
- **Azure OpenAI instead of Anthropic:** set `MODEL=azure_openai:gpt-4o`, set `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, and `OPENAI_API_VERSION` in `.env`, and run `pip install langchain-openai`.
