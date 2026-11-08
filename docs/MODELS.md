# Choosing the AI model (and cutting cost)

Expert Interviewer runs on an AI **model**, the "engine" that checks your documents, plays the witness, and grades you. You choose it on the setup page for each interview, from high-powered models to cheap ones, including free models that run on your own computer.

---

## Choosing a model on the setup page

1. Under **AI engine**, open the list. Models are grouped:
   - **High-powered:** the most capable models. Best quality, highest cost.
   - **Balanced:** strong models at moderate cost. The default, Claude Sonnet 5.5, is here.
   - **Cost-effective:** much cheaper models. Fine for practice, a little less polished.
   - **Free, runs on your computer:** models run by the free Ollama app. No bill, but slow without a powerful computer.
   - **Demo (no AI):** canned answers, for trying the screens.

   Each entry shows its company and a rough cost per interview.
2. **If a model isn't set up yet**, it's marked "needs setup". When you pick it, the page shows step-by-step instructions for exactly what's missing, such as getting an API key, adding it to the settings file, installing an add-on, or downloading a local model. After following them, click **Check again**. A newly saved API key works without restarting the app.
3. **Optional: use different models for different jobs.** Open **Use different models for different jobs** to pick a separate model for the witness, the document checker, the grading notes, and the grader. A good money-saver is a cheap model for the witness, which answers every question, and a strong one for the grader.
4. Click **Check documents & start interview.** The button is disabled until every chosen model is set up.

The results page shows which models played the witness and did the grading.

---

## Quick picks

| Goal | AI engine | Grader (under "different jobs") | Rough cost per interview* |
|---|---|---|---|
| **Default**, the setup the tool was built on | Claude Sonnet 5.5 | Same | ~$0.70 |
| **Best quality** | Claude Opus 5.5 or Claude Fable 5.1 | Same | ~$1.40 / ~$3.50 |
| **Budget mix (recommended for saving money)** | Claude Haiku 5.5 | Claude Sonnet 5.5 | ~$0.10–$0.25 |
| **Cheapest Claude** | Claude Haiku 5.5 | Same | ~$0.04 |
| **Free** | An Ollama model, e.g. gpt-oss 20B | A cloud model if grading struggles | $0 |

\* Rough estimates for a 15–25 question interview. Prices change; the list shows each model's price per million tokens, and the date it was last checked is in `models.json`.

**Tested so far:**
- **Claude Sonnet 5.5:** everything.
- **Claude Haiku 5.5:** everything, including grading.
- **Llama 3.2 3B on Ollama:** the document check and witness, both working but slow on an ordinary laptop (about a minute per answer).

All other models are untested. The prompts were written for Claude, so try a practice interview, such as the [Fastow example](../examples/enron-fastow/README.md), before relying on one.

---

## What's in the list

The list comes from [`models.json`](../models.json). Model names and prices were checked on each company's website on 2026-11-05.

| Company | Models listed |
|---|---|
| **Anthropic (Claude)** | Fable 5.1, Opus 5.5, Opus 5, Sonnet 5.5, Sonnet 5, Sonnet 4.6, Haiku 5.5 |
| **OpenAI** | GPT-6 Astra, GPT-6.1 Sol, GPT-6.1 Terra, GPT-6 Luna |
| **Google Gemini** | Gemini 4 Argon, Gemini 3.8 Flash, Gemini 3.5 Flash-Lite, Gemini 3.1 Flash-Lite |
| **xAI (Grok)** | Grok 4.7, Grok 4.3 |
| **DeepSeek** | DeepSeek V4 Pro, DeepSeek Flash (half price off-peak) |
| **Mistral** | Mistral Large, Mistral Small |
| **Ollama (free, local)** | gpt-oss 20B, Qwen3 32B, Qwen3 8B, Gemma 3 12B, Llama 3.1 8B, Llama 3.2 3B |

**A model that isn't listed:** choose **Other model (type its ID)** at the bottom of the list and type it as `provider:model-name`, e.g. `groq:<model-name>` or `ollama:mistral:7b`. The page checks it the same way. Groq is supported this way, but its current model list couldn't be confirmed, so no Groq models are pre-listed.

**Keeping the list current:** open `models.json` in Notepad or TextEdit to add, remove, or re-price models. Each entry has an `id`, a `label`, a `tier` (`high`, `balanced`, `economy`, `local`, or `demo`), a `price` (`[read, written]` in dollars per million tokens), and a `note`. Restart the app after editing.

---

## Setting up each company

The setup page walks you through these steps when you pick a model that needs them. They're collected here for reference.

| Company | What you need | Where to get it | Line to add to `.env` | Add-on |
|---|---|---|---|---|
| Anthropic | API key and credit | [console.anthropic.com](https://console.anthropic.com/settings/keys) | `ANTHROPIC_API_KEY=sk-ant-...` | Installed |
| OpenAI | API key and credit | [platform.openai.com](https://platform.openai.com/api-keys) | `OPENAI_API_KEY=sk-...` | Installed |
| Google Gemini | API key (billing for regular use) | [aistudio.google.com](https://aistudio.google.com/apikey) | `GOOGLE_API_KEY=AIza...` | Installed |
| xAI | API key and credit | [console.x.ai](https://console.x.ai/) | `XAI_API_KEY=xai-...` | Optional |
| DeepSeek | API key and balance | [platform.deepseek.com](https://platform.deepseek.com/api_keys) | `DEEPSEEK_API_KEY=sk-...` | Optional |
| Mistral | API key | [console.mistral.ai](https://console.mistral.ai/api-keys) | `MISTRAL_API_KEY=...` | Optional |
| Groq | API key | [console.groq.com](https://console.groq.com/keys) | `GROQ_API_KEY=gsk_...` | Optional |
| Ollama | The free Ollama app, running, plus the model downloaded | [ollama.com/download](https://ollama.com/download) | none | Installed |

**Adding a key to `.env`:**
1. Open the file named **.env** in the app folder.
   - **Windows:** right-click it → **Open with** → **Notepad**.
   - **Mac:** press **Cmd+Shift+.** to show hidden files, then open it with **TextEdit**.
2. If there's no `.env`, copy **.env.example** and rename the copy to **.env**.
3. Add the line from the table, with your key after the `=` sign and no spaces or quotes.
4. Save the file, then click **Check again** on the setup page.

**Turning on an "Optional" add-on:**
1. Open **requirements.txt** in the app folder.
2. Delete the `# ` at the start of that company's line, e.g. `# langchain-xai`.
3. Save, close the app window, and double-click the start file again. It installs the add-on, which takes 2–5 minutes.

**Downloading an Ollama model:**
1. With Ollama installed and running, open Terminal (Mac) or PowerShell (Windows).
2. Run `ollama pull <name>`, e.g. `ollama pull gpt-oss:20b`.
3. When it finishes, click **Check again**.

---

## Setting defaults in `.env` (optional)

The setup page starts with the models named in `.env`, so you don't have to pick them every time:

```
MODEL=anthropic:claude-haiku-5-5
MODEL_GRADER=anthropic:claude-sonnet-5-5
```

`MODEL` is the AI engine. `MODEL_WITNESS`, `MODEL_CHECKER`, `MODEL_CRITERIA`, and `MODEL_GRADER` pre-select the per-job models. Anything you choose on the setup page overrides these for that interview.

---

## What changes when you leave Claude

- **Thinking-effort settings are ignored.** Claude models think less for setup steps and more for grading; other models use their normal behavior.
- **No document caching.** With Claude, your documents are cached between questions, so re-reading them costs about a tenth as much. Other companies may cache automatically or not at all.
- **Prompts weren't tuned for them.** Other models may play the witness differently or grade more or less strictly.
- **Smaller models may fail** the steps that need a precise structured answer: the document check, the grading notes, and the grade. If grading fails, the app says so and lets you click **End & grade** again. For the next interview, pick a stronger grader.

---

## Troubleshooting

| What you see | What to do |
|---|---|
| A model says **needs setup** | Pick it to see the steps, follow them, then click **Check again**. |
| **Check again** still shows a missing key | Make sure the line in `.env` is spelled exactly as shown, saved, and has no spaces or quotes around the key. |
| An error mentioning **model not found** or **404** when the interview starts | The model name is wrong or retired. Update it in `models.json`, or check the company's current list. |
| **Grading didn't finish** | Click **End & grade** again. If it keeps failing, use a stronger grader next time. |
| Ollama models are very slow | Normal on laptops without a strong graphics chip. Use a smaller model, or a cloud model for the witness. |

---

## For developers

- **The catalog:** `models.json` is loaded by `model_catalog.py`.
  - `model_status(id)` reports readiness. A model is ready when its LangChain package is importable (`importlib.util.find_spec`), its key variable is set, and, for Ollama, `GET {OLLAMA_HOST}/api/tags` responds and lists the model.
  - `.env` is re-read (`load_dotenv(override=True)`) on every status check and session start.
- **Endpoints:**
  - `GET /models` returns the catalog with each model's status and the `.env` defaults.
  - `GET /models/status?id=` checks any model ID.
  - `POST /session/create` takes `models: {witness, checker, criteria, grader}` and returns 400 with a plain-English reason if any model isn't ready.
- **Agents:** each agent function takes its model string. `demo` (or `MOCK_LLM=1`) returns canned output.
  - Claude models get `reasoning_effort` per agent, `max_tokens=16000`, and a cached system prompt.
  - Structured output tries `method="json_schema"` first, then falls back to the provider's default.
- **Adding a provider:** add it to `providers` in `models.json` (`key_env`, `key_url`, `package`, `pip`, ...), add its package to `requirements.txt`, then add models.
