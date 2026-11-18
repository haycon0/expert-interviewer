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
| **Fastow (Enron): one question left** | A thorough interview of about 185 questions that closely follows the [interview outline](INTERVIEW-OUTLINE.md): full Upjohn warning, ground rules, documents identified before use, and a return to every key lead before the close. Only the final closing question is left. Presets **The C-Suite** with no variations. | Ask the closing question shown in the side panel (also saved in [`debug/scripts/fastow-final-question-closing.md`](../debug/scripts/fastow-final-question-closing.md)), then click **End & grade**. It averages **90 (Excellent)**. |
| **Fastow (Enron): mediocre, complete** | A finished, uneven interview (79 questions). | Click **End & grade**. It averages **69 (Needs coaching)**. |
| **Fastow (Enron): weak, complete** | A finished, weak interview (43 questions). | Click **End & grade**. It averages **60 (Needs practice)**. |

### Test scripts

These Fastow scripts each set up one situation. All are finished, so you click **End & grade** straight away (the wrong-input one stops at the document check first). They're built by `debug/tools/build_test_scripts.py`. What each test checks, and its results, are in [TESTING.md](TESTING.md).

| Script | What it is | What it shows |
|---|---|---|
| **test, interview ends early** | The opening, his role and the start of LJM1 (13 questions), then the interviewer has to stop and closes properly. | The interviewer ending early: **Incomplete**, rating only what was reached. |
| **test, interviewer ends late** | The strong interview through the Chewco buyout (156 questions); the last topic is opened, then the interviewer stops with no close. | The interviewer ending late: a normal score, with low Closing and related ratings. |
| **test, witness walks out** | The strong interview up to the Southampton confrontation (76 questions), where Fastow walks out; the interviewer stays calm and closes what it can. | The witness ending it: a normal score, never Incomplete, with no penalty for what the walk-out prevented. |
| **test, witness wants his own lawyer** | The strong interview up to his personal interests (61 questions); Fastow then stops for his own lawyer, and the interviewer handles it correctly. | The witness ending it: a normal score, with no penalty for the topics never reached. |
| **test, wrong input (stray payroll email)** | The mediocre interview, with an all-employee payroll reminder added to the case documents and shown to Fastow once. Don't tick **Skip the document check**. | The document check flags the email before the interview starts. |
| **test, missing Upjohn warning** | The strong, complete interview with the whole opening warning removed: no word on whom the lawyer represents, that they can't advise him, or who controls the privilege. | The missing warning caps the score at 59. |
| **test, missed follow-up (the LLC bonus)** | The strong, complete interview, except that at T15 Fastow mentions an LLC that paid staff bonuses for LJM work outside payroll, and it's never followed up. | The bonus payments appear under **Leads you didn't follow up**, with a question to ask. |
| **test, easy (cooperative witness)** and **test, hard (guarded witness)** | The same 34 questions, word for word. The cooperative Fastow volunteers facts; the guarded one gives the same facts only when pressed. | A side-by-side comparison of how a cooperative and a guarded witness answer the same interview. |

### Persona consistency test

`debug/tools/persona_test.py` checks that the three personas are noticeably different and stay in character. It puts the same 12 Fastow questions live to the witness once per persona (no variations). A judge model then rates each transcript's consistency (0–4, listing any turns that drift) and matches the three unlabeled transcripts to the persona descriptions. A run passes when every persona is rated 3 or more and all three are matched. Results go to `debug/gradings/persona-consistency_<run>.json`.

```
python debug/tools/persona_test.py 6 --witness anthropic:claude-sonnet-5-5
```

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
| `persona`, `variables`, `picks` | Optional presets: a persona name, and `"none"`, `"random"` or `"choose"`. With `"choose"`, `picks` lists the variations, for example `[{"name": "Cooperativeness", "value": "Guarded"}]`. |
| `resume_hint` | What to do next; shown in the side panel. |
| `transcript` | The exchanges so far, in order: `{"speaker": "expert" or "user", "message": "...", "mood": "..."}`. `mood` is optional and only used with the animated face. End with the witness's line if the interviewer should speak next. |

---

## For developers

- `debug.py` loads example cases (`debug/cases/`) and scripts (`debug/scripts/`), and holds the switch (`available()` is "not online"). Paths inside scripts must stay within the project folder. `GET /debug` serves the same page as `/` (404 when online); the page shows the Debugging box when its address is `/debug`. `/config` reports `debug_available`, which shows the **Debug page** link.
- `GET /debug/options` returns personas, variations, and scripts. `POST /session/create` accepts `debug: {case, script, persona, variables: "random"|"none"|"choose", picks: [{name, value}], twist, skip_check, rubric: "previous"}` (a script takes precedence over a case), and refuses it when the app is online.
- In `graph.py`, `initialize_session` honors the chosen persona and variations (`chosen_variables`), `verify_documents` skips the AI check when `skip_check` is set, and `start_interview` doesn't generate an opening line when a script has supplied the transcript.
