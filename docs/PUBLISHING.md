# Publishing Expert Interviewer to the internet

This guide puts the app on a public web address, protected by one shared password, using **Render**, a hosting service that runs the app straight from your GitHub repository. You don't need to touch a server or the command line.

**This guide is for the `online` branch**, the lower-cost version. **What you'll end up with:** a link like `https://expert-interviewer.onrender.com` that you share with your group, plus a password. Everyone uses your AI key, with a daily limit so a leaked password can't run up a big bill.

---

## What it costs

### Hosting

| Option | Monthly cost | Good for |
|---|---|---|
| **Render Free** | $0 | Trying it out. It **sleeps after 15 minutes** with no visitors (the next visit takes about a minute to wake it) and can restart at any time. A restart or sleep **ends any interview in progress**. |
| **Render paid, always on** (0.5 CPU / 512 MB) | Historically about **$7/month**. Render's pricing page didn't load when this was written, so confirm at [render.com/pricing](https://render.com/pricing). | A group using it regularly. Recommended once people rely on it. |
| Railway Hobby (alternative) | $5/month, which includes $5 of usage | Similar ease; billed by usage. |
| Fly.io (alternative) | About $3.69–$4.39/month for the smallest 512 MB machine; no free tier | Cheapest always-on, with more setup. |

A secure (HTTPS) address is included free with Render, so voice works in the browser. A custom domain name (e.g. `interviews.yourname.com`) is optional, and you buy it separately from a domain registrar.

### AI usage (billed by Anthropic to your key)

This version uses **Claude Haiku**, Anthropic's lowest-cost model, for everything: roughly **$0.02–$0.05 per interview**. With the daily cap of 10 interviews, the most it can cost is about **$0.50 a day**.

It offers only the lower-cost options on purpose: Haiku (or other economical models whose keys you add), the browser's built-in voice, and the animated face. Visitors who want more capable models, natural voices, or lifelike faces are pointed to the full version, which they can set up on their own computer with their own accounts.

Most groups will spend far less than the cap. The voice and face in this version are free.

**Also set a spending limit with Anthropic** as a backstop: in the [Anthropic Console](https://console.anthropic.com/), go to **Limits** (or **Billing**) and set a monthly limit.

---

## Before you start

- **Your code must be on GitHub,** including the latest changes; Render reads it from there. If you haven't pushed recently, push first (Claude can do this for you).
- **A private GitHub repository works.** Render asks for permission to read it.
- **Your API key is never in the repository.** `.env` is excluded from git, and you'll paste the key into Render's settings instead.

---

## Step by step

### 1. Create a Render account
Go to **https://render.com**, click **Get Started**, and sign up with your GitHub account. That's the easiest way to give Render access to your repository.

### 2. Create the service from the Blueprint
1. In the Render dashboard, click **New +** → **Blueprint**.
2. Connect your GitHub account if asked, and pick the **expert-interviewer** repository. When asked for a branch, choose **online**: that's this lower-cost version. (The **local** branch is the full version for personal computers; don't publish it, since it would let visitors use expensive options on your key.)
3. Render reads `render.yaml` from the repository and shows a service named **expert-interviewer**. Click **Apply** (or **Deploy Blueprint**).

### 3. Enter the two secrets
Render asks for the values marked as secret:

| Setting | What to enter |
|---|---|
| `APP_PASSWORD` | The password your group will use. Pick something long, like four random words (`maple-rocket-quiet-harbor`). |
| `ANTHROPIC_API_KEY` | Your Anthropic API key (starts with `sk-ant-`). |

Everything else is pre-filled: Claude Haiku as the model, the daily limit of 10 interviews, the limit of 60 questions per interview, and not saving interviews on the server.

### 4. Wait for the first deploy
Render installs everything and starts the app, which takes a few minutes. When the status shows **Live**, click the link at the top of the page (it ends in `.onrender.com`).

### 5. Sign in and test
You'll see a sign-in page. Enter your password and run a short interview. The **Sign out** link is at the top right.

### 6. Share it
Send your group the link and the password, ideally separately (e.g. the link by email and the password in person or by text).

---

## Running it day to day

| To... | Do this in the Render dashboard |
|---|---|
| **Change the password** (e.g. if it leaked) | Your service → **Environment** → edit `APP_PASSWORD` → **Save**. Everyone is signed out and needs the new one. |
| **Raise or lower the daily limit** | Edit `MAX_INTERVIEWS_PER_DAY` (blank or `0` means no limit). |
| **Offer another low-cost model** | Add that provider's key under **Environment** (e.g. `GOOGLE_API_KEY` for Gemini Flash-Lite). Models appear on the setup page once their key is set. |
| **Stop it from sleeping** | Your service → **Settings** → **Instance Type** → choose a paid, always-on instance. |
| **Update the app** | Push changes to GitHub. Render redeploys automatically (`autoDeployTrigger: commit`). |
| **Take it offline** | Your service → **Settings** → **Suspend Service** (or delete it). |

---

## How it's protected

- **Password on everything.** Every page and every request needs the shared password, except a basic health check that reveals nothing.
  - Logins last 7 days, in a secure, browser-only cookie.
  - After 10 wrong passwords in 15 minutes, that visitor has to wait.
- **It won't run open by accident.** If the app is on Render (or has `ALLOWED_HOSTS` set) but no `APP_PASSWORD` is set, it refuses to serve anything.
- **Spending limits.** At most `MAX_INTERVIEWS_PER_DAY` new interviews per day and `MAX_QUESTIONS_PER_INTERVIEW` questions each, plus your Anthropic spending limit.
- **Only its own address.** The app answers only to its Render address (and any in `ALLOWED_HOSTS`).

**Limitations to know:**
- **The daily count resets on restart.** It's kept in memory, so a restart starts it again at zero. Render Free restarts often, so rely on your Anthropic spending limit too.
- **One shared password.** Anyone who has it can use the app, and you can't tell users apart or remove just one person without changing the password for everyone.
- **Everyone shares one server.** People can't see each other's interviews, but anyone with the password and the app can start interviews on your key.

---

## Privacy: think before using real case material

Online, uploaded documents and conversations pass through **Render's servers** as well as the AI provider. The app doesn't save interviews to disk there (`SAVE_SESSIONS=0`), but they're held in memory while it runs. Before using real confidential or privileged material, check your organization's rules on cloud hosting and AI services. For practice with public material like the included Enron example, this isn't a concern.

---

## What works differently online

- **Free local models (Ollama) don't work.** They run on your own computer, not on the server. Use the cloud models.
- **Interviews aren't saved after they end**, and on Render Free they can be cut off by a restart.
- **Voice needs a secure address.** Render's `https://` address provides one, so the microphone works.

---

## Troubleshooting

| What you see | What to do |
|---|---|
| The deploy fails during "Build" | Open the deploy's logs in Render and look for the first error line. A typo in `requirements.txt` is the usual cause. |
| **This app is online without a password, so it's switched off** | Add `APP_PASSWORD` under **Environment** and save. |
| **Invalid host header** | You're using an address the app doesn't know, such as a custom domain. Add it to `ALLOWED_HOSTS` (comma-separated) under **Environment**. |
| The page takes about a minute to load | Render Free was asleep. Upgrade to an always-on instance to avoid this. |
| **The daily limit … has been reached** | Wait until midnight UTC, or raise `MAX_INTERVIEWS_PER_DAY`. |
| **That password isn't right** for everyone | Check `APP_PASSWORD` in Render for extra spaces; save it again if needed. |

---

## For developers

- **Access control:** `access.py`, added in `server.py` as HTTP middleware.
  - Uses `APP_PASSWORD`, an optional `SESSION_SECRET`, `MAX_INTERVIEWS_PER_DAY`, `MAX_QUESTIONS_PER_INTERVIEW`, and `ALLOWED_HOSTS`.
  - Render's `RENDER` and `RENDER_EXTERNAL_HOSTNAME` are picked up automatically.
- **The login cookie:** `{expiry}.{HMAC-SHA256}`, keyed on the password, so changing the password revokes every login.
- **Deployment config:** `render.yaml` holds the Blueprint, and `.python-version` pins Python 3.14, the version tested.
- **Proxy headers:** the start command passes `--proxy-headers --forwarded-allow-ips="*"`, so the app sees HTTPS and real client IPs behind Render's proxy.
- **Health check:** `/healthz`.
