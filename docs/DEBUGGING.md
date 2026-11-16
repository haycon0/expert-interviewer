# The debug page

The debug page (`/debug`) lets you test the app without running a whole interview from scratch each time. You can:

- **skip typing in a case:** the Enron example (witness, role, background, and its events log) is filled in for you,
- **choose the witness's persona** instead of getting a random one,
- **choose its variations** (or have none) instead of random ones,
- **start from a script**, a case and an interview already in progress, so you can test the second half, the end, or grading right away,
- **skip the document check** to save time and money.

In a debug interview, the persona and its variations are always shown in the side panel.

---

## Opening the debug page

Debugging has its own page. Click **Debug page** at the top right of the setup page, or go to `http://localhost:8000/debug`. On that page:
1. **The Debugging box is shown** under the heading, with the options below.
2. **The Enron example is filled in:** the witness's name (Andrew Fastow), role, and case background. Its events log is listed under **Case documents** as *added automatically on the debug page*. The app attaches it when the interview starts, because a web page can't fill in the file chooser itself.
3. **Choose your options** and click **Check documents & start interview**.

To use the app normally, click **Leave the debug page** (or go to `http://localhost:8000/`). The regular page has no debugging options at all.

**It can't be used online.** When the app runs on a hosting service (or with `ALLOWED_HOSTS` set), the **Debug page** link doesn't appear, `/debug` shows "not found", and the server refuses debug requests, so nobody using a published site can see or choose the hidden persona.

---

## The Debugging box

| Option | What it does |
|---|---|
| **Example case** | The case filled in for you: **Enron (Andrew Fastow)** by default, or **None** to enter your own. You can also upload extra files; they're added alongside the case's documents. |
| **Start from a script** | Loads a prepared case and interview. The witness's name, role, and case background are filled in, and the script's documents are added automatically. The interview opens partway through, with the earlier exchanges in the transcript. The side panel tells you where to pick up. |
| **Persona** | **Random** (normal behavior), or one of the personas in `personas.json`. A script may preset one; you can change it. |
| **Variations** | **Random** (normal), **None**, or **Choose**: pick an option for any of the categories in `variables.json` and whether to include the persona's own twist. |
| **Skip the document check** | Marks every document as relevant without asking the AI. Faster and cheaper; use it when you're not testing the check itself. |
| **Grading rubric** | **Rubric v2.2** (normal), or the **previous rubric** (draft 2, scored 0–100 with letter grades) to compare the two on the same kind of interview. |

The scripted lines are pre-written, so starting from a script costs nothing until you ask your first new question.

---

## The included scripts

| Script | Where it starts | What to do |
|---|---|---|
| **Fastow (Enron): halfway** | After 8 exchanges: the opening warning, background, LJM1, and Fastow committing to what he told the Board. | Continue at question 11 of the [Fastow example](../examples/enron-fastow/README.md) (the Rhythms unwind), then confront him with Southampton Place. |
| **Fastow (Enron): one question left** | A thorough interview of about 175 questions that closely follows the [interview outline](INTERVIEW-OUTLINE.md) (full Upjohn warning, ground rules, documents identified before use), with only the final closing question left. Presets **The C-Suite** with no variations. | Ask the closing question shown in the side panel (also saved in [`debug/scripts/fastow-final-question-closing.md`](../debug/scripts/fastow-final-question-closing.md)), then click **End & grade**. With rubric v2.2 it scored **92 and 96 (Excellent)** on Claude Haiku. If his answer to the closing question opens something new, follow it up before ending. |
| **Fastow (Enron): mediocre, complete** | A finished, uneven interview (79 questions). | Click **End & grade**. Graded 78, 70, 69 on Claude Haiku. |
| **Fastow (Enron): weak, complete** | A finished, weak interview (43 questions). | Click **End & grade**. Graded 65, 66, 67 on Claude Haiku. |
| **Fastow (Enron): strong, with poor prioritization** | The strong interview, finished, plus a 31-question detour into low-value topics (the aircraft lease, the stock split, the Gaza project) before the key issues. | Click **End & grade**. Graded 94, 87, 89 on Claude Haiku, the same as without the detour: the rubric doesn't consider use of time. See [`debug/gradings/PRIORITIZATION.md`](../debug/gradings/PRIORITIZATION.md). |

The strong, mediocre and weak interviews were each graded three times to test consistency; the results are in [`debug/gradings/`](../debug/gradings/README.md).

---

## Adding your own example case

Example cases are JSON files in `debug/cases/`. Copy `enron-fastow.json` and edit it: `name`, `description`, `expert_name`, `expert_role`, `case_background` or `case_background_file`, and `documents` (paths inside the project folder). Add `"default": true` to make it the one filled in when the debug page opens.

## Writing your own script

Scripts are JSON files in `debug/scripts/`. Copy an existing one and edit it. The fields:

| Field | Meaning |
|---|---|
| `name`, `description` | Shown in the Debugging box. |
| `expert_name`, `expert_role` | Fill in the setup page. |
| `case_background` or `case_background_file` | The background text, or a path to a text file inside the project folder. |
| `documents` | Paths to case documents inside the project folder (PDF, Word, or text). A script brings its own case, so the example case isn't used with it. |
| `persona`, `variables` | Optional presets: a persona name, and `"none"` or `"random"`. |
| `resume_hint` | What to do next; shown in the side panel. |
| `transcript` | The exchanges so far, in order: `{"speaker": "expert" or "user", "message": "...", "mood": "..."}`. `mood` is optional and only used with the animated face. End with the witness's line if the interviewer should speak next. |

---

## For developers

- `debug.py` loads example cases (`debug/cases/`) and scripts (`debug/scripts/`), and holds the switch (`available()` is "not online"). Paths inside scripts must stay within the project folder. `GET /debug` serves the same page as `/` (404 when online); the page shows the Debugging box when its address is `/debug`. `/config` reports `debug_available`, which shows the **Debug page** link.
- `GET /debug/options` returns personas, variations, and scripts. `POST /session/create` accepts `debug: {case, script, persona, variables: "random"|"none"|"choose", picks: [{name, value}], twist, skip_check, rubric: "previous"}` (a script takes precedence over a case), and refuses it when the app is online.
- In `graph.py`, `initialize_session` honors the chosen persona and variations (`chosen_variables`), `verify_documents` skips the AI check when `skip_check` is set, and `start_interview` doesn't generate an opening line when a script has supplied the transcript.
