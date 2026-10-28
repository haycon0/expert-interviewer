# Setting up Expert Interviewer

This guide assumes you have never written code or used a programming tool. If you can download a file and install an app, you can do this. It takes about 15 minutes the first time.

**What you'll do:**

1. Install Python (a free program the app needs to run)
2. Download Expert Interviewer
3. Get an Anthropic API key (lets the app use the Claude AI model)
4. Double-click a file to start the app

You only do steps 1–3 once. After that, starting the app is just step 4.

---

## Step 1: Install Python

Python is a free program that runs the app behind the scenes. You won't need to use it directly.

### Windows

1. Go to **https://www.python.org/downloads/** and click the big yellow **Download Python** button.
2. Open the file you downloaded (it's usually in your **Downloads** folder).
3. **Important:** on the first screen of the installer, tick the box at the bottom that says **"Add python.exe to PATH"**. If you skip this, the app won't be able to find Python.
4. Click **Install Now** and wait for it to finish, then click **Close**.

### Mac

1. Go to **https://www.python.org/downloads/** and click the big yellow **Download Python** button.
2. Open the downloaded file and click **Continue** / **Agree** / **Install** through the installer, using the default options.
3. When it finishes, a Finder window may open. You can close it.

---

## Step 2: Download Expert Interviewer

1. Go to the project page on GitHub: **https://github.com/haycon0/expert-interviewer**
   - If you see "404 – Page not found", the project is private. Ask the owner to invite you; GitHub will email you the invitation, and you'll need a free GitHub account to accept it.
2. Click the green **Code** button near the top right of the file list.
3. Click **Download ZIP** at the bottom of the menu that appears.
4. Unzip it:
   - **Windows:** open your Downloads folder, right-click **expert-interviewer-main.zip**, choose **Extract All…**, then click **Extract**.
   - **Mac:** open your Downloads folder and double-click **expert-interviewer-main.zip**.
5. You now have a folder called **expert-interviewer-main**. Move it somewhere easy to find, such as your Desktop.

> **Tip:** "GitHub" is a website where people share projects. A "repository" (or "repo") is one project on it. You don't need an account to download a public one.

---

## Step 3: Get an Anthropic API key

An API key is like a password that lets the app use Anthropic's Claude AI model, and it's how Anthropic bills you for that use. Using the app costs money: roughly **$0.40–$0.75 per practice interview**. You prepay a small amount of credit.

1. Go to **https://console.anthropic.com/** and sign up (or log in).
2. Find **Billing** in the menu and add credit. $5 is plenty to start; that's roughly 7–12 interviews.
3. Find **API Keys** in the menu and click **Create Key**. Give it any name, such as "Expert Interviewer".
4. **Copy the key right away** and keep it somewhere private, such as a password manager. It starts with `sk-ant-`. Anthropic shows it only once. If you lose it, just create a new one.

> **Keep your key private.** Anyone who has it can spend your credit. Don't email it, post it, or put it in a shared document.

**Just want to look around first?** You can skip this step. The app has a **demo mode** with canned answers that costs nothing, so you can click through every screen. You can add a key later.

---

## Step 4: Start the app

### Windows

1. Open the **expert-interviewer-main** folder.
2. Double-click **start** (it may show as **start.bat**, with a gear icon).
3. If a blue box says **"Windows protected your PC"**, click **More info**, then **Run anyway**. Windows shows this for any downloaded file it doesn't recognize.
4. A black window opens. **The first time only**, it spends 1–3 minutes installing what the app needs. Wait until it asks for your key.
5. When it says **API key:**, paste your key (**right-click** inside the black window to paste) and press **Enter**. Or just press **Enter** to use demo mode.
6. Your web browser opens the app after a few seconds.

### Mac

1. Open the **expert-interviewer-main** folder.
2. **Right-click** (or Control-click) **start.command** and choose **Open**.
3. If a message says it's from an unidentified developer, click **Open**. (Double-clicking the first time may only offer **Cancel**; that's why you right-click.)
4. A Terminal window opens. **The first time only**, it spends 1–3 minutes installing. Wait until it asks for your key.
5. When it says **API key:**, paste your key (**Cmd+V**) and press **Return**. Or just press **Return** to use demo mode.
6. Your web browser opens the app after a few seconds.

### While you use the app

- **Leave the black (Windows) or Terminal (Mac) window open.** That window *is* the app running. Closing it stops the app.
- The app lives at **http://127.0.0.1:8000** in your browser. It runs only on your computer; nobody else can see it.
- The top-right corner of the app shows **"Model: anthropic:claude-sonnet-5-5"** when your key is working, or **"Mock mode (no API key)"** in demo mode.

### Next time

Just double-click **start** (Windows) or **start.command** (Mac) again. It skips the installing and opens straight away.

---

## Step 5: Try the practice interview

The **examples/enron-fastow** folder has a complete practice run. You interview Andrew Fastow, the former CFO of Enron, as an investigator. Open **README.md** in that folder (you can read it on the GitHub website too: click **examples**, then **enron-fastow**). It tells you exactly what to type into each box, which file to upload, and 30 questions to ask.

---

## Using the app

1. **Witness name:** the employee you're interviewing.
2. **Role and company:** optional, e.g. "CFO, Enron Corp."
3. **Case background:** a few sentences on the complaint or suspected misconduct.
4. **Case file:** optional. Upload a text file of evidence, such as an events log or notes. Only .txt, .csv, .md, and .json files work, not PDFs or Word documents.
5. Click **Research & start interview** and wait about 30 seconds while the app researches the witness.
6. Type questions in the box at the bottom and press **Enter** to send. The right side shows the witness file the app prepared, plus the grading criteria.
7. When you're done, click **End & grade**. You get a score, feedback on each criterion, missed opportunities, and coaching. The witness's hidden personality is revealed here.

---

## If something goes wrong

| What you see | What to do |
|---|---|
| **"Python is not installed, or Windows can't find it"** | Reinstall Python (Step 1) and make sure you tick **"Add python.exe to PATH"**. Then restart your computer and try again. |
| **"Setup failed"** | Check your internet connection and double-click the start file again. If you're on a work or school network, try a home network; some block software downloads. |
| Browser shows **"This site can't be reached"** | The app may still be starting. Wait 10 seconds and refresh the page. Check that the black/Terminal window is still open. |
| App says **"Mock mode (no API key)"** but you entered a key | Delete the file named **.env** in the app folder (on Mac, press **Cmd+Shift+.** to show hidden files), then start the app again and re-enter your key. |
| Error when starting an interview, mentioning **credit** or **billing** | Add credit in the Anthropic Console (Step 3). |
| Error mentioning **authentication** or **invalid x-api-key** | The key was mistyped or deleted. Delete **.env** as above and enter the key again. |
| You typed `start` in PowerShell and it asks for **FilePath:** | PowerShell has its own `start` command. Press **Ctrl+C**, then type `.\start.bat` and press Enter. Or just double-click **start.bat** in File Explorer. |
| **"Address already in use"** in the black/Terminal window | The app is already running in another window. Use that one, or close all of them and start again. |
| On Mac, nothing happens when you open **start.command** | Open the **Terminal** app (search for it with Cmd+Space), type `bash ` (with a space), drag **start.command** into the Terminal window, and press Return. |
| Sessions disappear after you close the app | That's expected in this version. Each interview lasts only while the app is running. |

---

## Changing how the app works (optional)

These files can be opened and edited with **Notepad** (Windows) or **TextEdit** (Mac). Close and restart the app after any change.

- **rubric.json:** the grading criteria, their weights (must add up to 100), and what each score level means.
- **personas.json:** the witness personalities the app picks from at random.

Keep the punctuation (quotes, commas, brackets) exactly as it is; only change the words inside the quotes. If the app stops starting after an edit, download a fresh copy of the file from GitHub.

---

## For developers

Prefer the command line? Clone the repo, create a virtual environment, `pip install -r requirements.txt`, copy `.env.example` to `.env` and add your key, then run `python -m uvicorn server:app --reload`. Set `MODEL` in `.env` to switch models (e.g. `azure_openai:gpt-4o` with `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `OPENAI_API_VERSION`, and `pip install langchain-openai`). Per-agent speed/cost settings are in the `EFFORT` table in `agents.py`.
