# Choosing the AI model (and cutting cost)

Expert Interviewer runs on an AI **model**, the "engine" that reads your documents, plays the witness, and grades you. By default every part of the tool uses **Claude Sonnet 5.5** from Anthropic. You can switch to a cheaper model, use different models for different jobs, or use another company's models.

You change the model by editing one small settings file. No coding needed.

---

## Quick picks

| Option | Rough cost per interview* | What to expect |
|---|---|---|
| **Claude Sonnet 5.5** (the default) | $0.40–$0.80 | The setup the tool was built and tested on. |
| **Budget mix:** Claude Haiku 5.5 for everything except grading, Sonnet 5.5 for grading | $0.10–$0.25 | **Recommended if cost matters.** Fast, cheap witness replies, with careful grading. Tested. |
| **Claude Haiku 5.5 for everything** | $0.02–$0.05 | About 20 times cheaper than Sonnet. Tested as the witness and document checker; its acting is a little less polished. Grading on Haiku hasn't been tested and may be less careful. |
| **Claude Opus 5.5** | $0.80–$1.60 | Anthropic's top everyday model. Best quality, about twice Sonnet's price. |
| **Other companies** (OpenAI, Google Gemini, Groq, DeepSeek, Mistral, xAI) | Varies, often low | Works with the tool, but **not tested** with it. Quality and cost depend on the model you pick. |
| **Ollama** (runs on your own computer) | Free | No API bill, but needs a fairly powerful computer. Small models often fail the tool's structured steps (document check, grading). Not tested. |

\* Estimates for a 15–25 question interview, based on Anthropic's prices as of October 2026 (per million tokens, read / written: Haiku 5.5 $0.10 / $0.50, Sonnet 5.5 $2 / $10, Opus 5.5 $4 / $20). Check [anthropic.com/pricing](https://www.anthropic.com/pricing) for current prices. A token is about three-quarters of a word.

**Where the money goes:** the witness answers every question, so it makes far more AI calls than anything else. The grader runs once but thinks hard. That's why the budget mix keeps Sonnet only for grading.

---

## How to change the model

### Step 1: Open the settings file

The settings live in a file named **`.env`** in the app folder. The start file creates it when you enter your API key.

- **Windows:** open the app folder, right-click **.env**, choose **Open with** → **Notepad**.
- **Mac:** open the app folder and press **Cmd+Shift+.** (period) to show hidden files. Right-click **.env** → **Open With** → **TextEdit**.

**No `.env` file?** You probably pressed Enter at the key prompt to use demo mode. Make a copy of **`.env.example`** in the same folder and rename the copy to **`.env`**. Windows may warn about changing the extension; click **Yes**.

### Step 2: Change or add lines

The file looks something like this:

```
ANTHROPIC_API_KEY=sk-ant-...
MODEL=anthropic:claude-sonnet-5-5
```

Change the `MODEL=` line, or add lines from the recipes below. A model is always written as **`provider:model-name`**, with no spaces and no quotes.

### Step 3: Save and restart

Save the file (Ctrl+S or Cmd+S), close the app's black or Terminal window, and double-click the start file again.

### Step 4: Check it worked

The top-right corner of the app shows the main model, e.g. **Model: anthropic:claude-haiku-5-5**. If some agents use a different model, it adds "(some agents use other models)". If a model's API key is missing, a **Setup problem** message appears on the setup page.

---

## Recipes

Copy the lines into `.env`, replacing any `MODEL` lines already there. Keep your API key line.

### Budget mix (recommended for saving money)

```
ANTHROPIC_API_KEY=sk-ant-...
MODEL=anthropic:claude-haiku-5-5
MODEL_GRADER=anthropic:claude-sonnet-5-5
```

### Cheapest Claude

```
ANTHROPIC_API_KEY=sk-ant-...
MODEL=anthropic:claude-haiku-5-5
```

### Best quality

```
ANTHROPIC_API_KEY=sk-ant-...
MODEL=anthropic:claude-opus-5-5
```

### OpenAI (ChatGPT's company)

1. Get a key at [platform.openai.com](https://platform.openai.com/) → **API keys**, and add credit under **Billing**.
2. Pick a model from OpenAI's [pricing page](https://openai.com/api/pricing/). Small "mini" models are the cheapest.

```
OPENAI_API_KEY=sk-...
MODEL=openai:gpt-4o-mini
```

### Google Gemini

1. Get a key at [aistudio.google.com](https://aistudio.google.com/) → **Get API key**.
2. Pick a model from Google's [Gemini pricing page](https://ai.google.dev/pricing). "Flash" models are the cheapest.

```
GOOGLE_API_KEY=AIza...
MODEL=google_genai:gemini-2.5-flash
```

### Ollama (free, on your own computer)

1. Install Ollama from [ollama.com](https://ollama.com/).
2. Open Terminal (Mac) or PowerShell (Windows) and download a model, e.g. `ollama pull llama3.2`. Browse models at [ollama.com/library](https://ollama.com/library). Bigger models work better but need more memory.
3. Keep Ollama running while you use the app.

```
MODEL=ollama:llama3.2
```

No API key is needed.

> **Model names change often.** The OpenAI, Gemini, and Ollama names above are examples. If the app says a model wasn't found, look up the current name on that company's pricing or model page.

---

## Using different models for different jobs

`MODEL` sets the model for everything. You can override it for any of the four agents by adding these lines:

| Setting | Agent | How often it runs | Good place to save? |
|---|---|---|---|
| `MODEL_WITNESS` | Plays the witness | Every question, plus the opening line | **Yes, the biggest saving** |
| `MODEL_CHECKER` | Checks each uploaded document | Once per document | Yes |
| `MODEL_CRITERIA` | Writes the hidden case-specific grading notes | Once per interview | Yes |
| `MODEL_GRADER` | Scores your interview and coaches you | Once per interview | Keep a strong model here for reliable grades |

For example, to keep Sonnet everywhere but use Haiku for the witness:

```
ANTHROPIC_API_KEY=sk-ant-...
MODEL=anthropic:claude-sonnet-5-5
MODEL_WITNESS=anthropic:claude-haiku-5-5
```

You can mix companies, too. Each one just needs its own key line.

---

## All supported providers

| Provider | Write `MODEL=` as | Key line in `.env` | Where to get a key | Installed? |
|---|---|---|---|---|
| Anthropic (Claude) | `anthropic:claude-...` | `ANTHROPIC_API_KEY=` | [console.anthropic.com](https://console.anthropic.com/) | Yes |
| OpenAI | `openai:...` | `OPENAI_API_KEY=` | [platform.openai.com](https://platform.openai.com/) | Yes |
| Google Gemini | `google_genai:...` | `GOOGLE_API_KEY=` | [aistudio.google.com](https://aistudio.google.com/) | Yes |
| Ollama (local) | `ollama:...` | none | [ollama.com](https://ollama.com/) (install the app) | Yes |
| Groq | `groq:...` | `GROQ_API_KEY=` | [console.groq.com](https://console.groq.com/) | Optional |
| DeepSeek | `deepseek:...` | `DEEPSEEK_API_KEY=` | [platform.deepseek.com](https://platform.deepseek.com/) | Optional |
| Mistral | `mistralai:...` | `MISTRAL_API_KEY=` | [console.mistral.ai](https://console.mistral.ai/) | Optional |
| xAI (Grok) | `xai:...` | `XAI_API_KEY=` | [console.x.ai](https://console.x.ai/) | Optional |
| Azure OpenAI | `azure_openai:...` | `AZURE_OPENAI_API_KEY=`, plus `AZURE_OPENAI_ENDPOINT=` and `OPENAI_API_VERSION=` | your organization's Azure portal | Yes |

**To turn on an "Optional" provider:**

1. Open **`requirements.txt`** in the app folder with Notepad or TextEdit.
2. Find its line near the bottom, e.g. `# langchain-groq`, and delete the `# ` at the start.
3. Save, then restart the app. The start file notices the change and reinstalls (2–5 minutes).

---

## What changes when you leave Claude

These features only work with Anthropic models. With other providers the tool still runs, but:

- **Thinking-effort settings are ignored.** Each agent's effort level (low for setup, high for grading) only applies to Claude.
- **No document caching.** With Claude, your documents are cached between questions so re-reading them costs about a tenth as much. Other providers may cache automatically or not at all, depending on the provider.
- **Prompts weren't tuned for them.** The witness and grader instructions were written and tested with Claude. Other models may play the witness differently or grade more or less strictly. Run a practice interview, such as the [Fastow example](../examples/enron-fastow/README.md), before relying on one.
- **Smaller models may fail** the steps that need a precise structured answer: the document check, the grading notes, and the grade. If you see errors at those steps, set `MODEL_CHECKER`, `MODEL_CRITERIA`, and `MODEL_GRADER` to a stronger model.

---

## Troubleshooting

| What you see | What to do |
|---|---|
| **Setup problem: … needs … in .env** | That model's API key line is missing. Add it (see the table above) and restart. |
| An error mentioning **model not found** or **404** | The model name is wrong or retired. Check the current name on the provider's site. |
| An error mentioning **No module named langchain_…** | That provider is optional and not installed. Uncomment its line in `requirements.txt`, then restart. |
| Errors when checking documents or grading, on a small or local model | Use a stronger model for `MODEL_CHECKER` and `MODEL_GRADER`. |
| **Connection refused** with Ollama | Ollama isn't running. Open the Ollama app and try again. |
| The app still shows the old model | Make sure you saved `.env`, then fully close the app window and start it again. |

---

## For developers

- **Where it's handled:** model selection is in `agents.py`.
  - `MODEL` is the default model, and `AGENT_MODEL_VARS` maps each agent to its override variable (`verify` → `MODEL_CHECKER`, `greeting`/`expert` → `MODEL_WITNESS`, `rubric` → `MODEL_CRITERIA`, `grader` → `MODEL_GRADER`).
  - Models are created with LangChain's `init_chat_model` and cached per `(model, effort)`.
- **Anthropic-only features:** `reasoning_effort` and the cached system prompt (`cache_control`) are applied only to `anthropic:` models.
- **Structured output:** `with_structured_output(method="json_schema")` is tried first, falling back to the provider's default method if that one isn't supported.
- **Demo mode:** `_KEY_BY_PROVIDER` maps providers to their key variables. Demo mode turns on when `MODEL`'s key is missing. A missing key for an override is reported in `/config` as `warnings`.
- **Adding a provider:** add its `langchain-*` package to `requirements.txt`, and its key variable to `_KEY_BY_PROVIDER`. Any provider that `init_chat_model` supports will work.
