# Voice and face

> **On the online version** only the lower-cost options are available. This guide describes the full version, which you can run on your own computer with your own accounts: see the [`local` branch](https://github.com/haycon0/expert-interviewer/tree/local) and its [setup directions](https://github.com/haycon0/expert-interviewer/blob/local/SETUP.md).


You can interview the witness three ways. Choose under **Conversation** on the setup page:

| Mode | What happens | Needs |
|---|---|---|
| **Text** (default) | You type questions; the witness types answers. | Nothing extra |
| **Voice** | You click **Talk** and ask out loud; the witness answers out loud. The written transcript is hidden unless you click **Show transcript**. | A voice service: the free browser one, or a paid one |
| **Voice + face** | Voice, plus a face that reacts while the witness talks. | A voice service and a face |

---

## Quick start (free)

1. Open the app in **Chrome** or **Edge**.
2. Under **Conversation**, pick **Voice + face**.
3. Leave **Voice service** on **Browser built-in (free)** and **Face** on **Animated face (free)**. Click **Hear it** to try the voice.
4. Start the interview as usual. On the interview screen, turn your sound on and click **Start the conversation**.
5. Click **Talk**, ask your question, then click **Stop**. Your question is sent automatically. The witness answers out loud while its face moves.
6. The first time, your browser asks to use the microphone. Click **Allow**.

A status line under the face says what's happening: listening, thinking, speaking, or an error. The written transcript is hidden in voice modes so it feels like a real conversation. Your spoken questions are sent straight to the witness without appearing in the question box. Click **Show transcript** at the top to see the conversation in the side bar; while it's showing, your words also appear in the box as you speak. Click **Hide transcript** to put it away. You can still type at any time, and **End & grade** works the same in every mode.

---

## The options

### Voice services

The voice service does two jobs: **hearing you** (turning your speech into text) and **speaking** as the witness.

| Service | Cost (as listed on 2026-11-08) | Notes |
|---|---|---|
| **Browser built-in** | Free | Chrome or Edge only for hearing you. Voices sound robotic. Your speech is processed by the browser maker's servers (Google for Chrome), so be careful with confidential material. |
| **OpenAI** | Hearing: $0.0045/minute. Speaking: $12 per million audio tokens (roughly $0.25–$0.50 per interview) | Natural voices. 13 to choose from. |
| **ElevenLabs** | Speaking: $0.04 per 1,000 characters. Hearing: $0.22/hour | The most lifelike voices; your account's voices appear in the list. |
| **Deepgram** | Hearing: $0.0043/minute. Speaking: $0.030 per 1,000 characters. $200 free credit for new accounts | Fast and inexpensive. |

A typical 20–30 minute interview adds roughly **$0.25–$0.85** with a paid voice service, on top of the AI model's cost.

### Faces

| Face | Cost (as listed on 2026-11-08) | Notes |
|---|---|---|
| **Animated face** | Free | A cartoon face drawn in your browser. It blinks, its mouth moves while it talks, and its expression changes with the witness's mood. Works with any voice service. |
| **Simli** | From $0.009/minute; free plan with 50 minutes a month | A lifelike face lip-synced to the witness's voice. **Needs OpenAI, ElevenLabs, or Deepgram as the voice service.** Simli's site showed its API as temporarily paused on 2026-11-05. |
| **D-ID** | Not confirmed | Animates a photo you provide and speaks with D-ID's own voice. D-ID now labels this API "legacy". |
| **Tavus** | Plans from $59/month (175 minutes); about $0.26–$0.37 per extra minute | Polished lifelike video with Tavus's own voice. |
| **HeyGen** | Not confirmed | **Experimental.** HeyGen's current documentation couldn't be reached, so this follows its older Streaming Avatar documentation and will likely need fixes. |

With D-ID, Tavus, and HeyGen the face speaks in its own voice. Your chosen voice service is then only used for hearing you.

**How the face shows emotion:** with a face on, the witness labels each answer with a mood (neutral, calm, friendly, confident, thoughtful, nervous, defensive, annoyed, evasive, or surprised). The animated face shows it with its eyebrows, eyes, and mouth, and the mood name appears under the face. The label is never shown in the transcript or spoken. Lifelike faces take their expression from the voice instead.

---

## Setting up a paid option

When you pick an option that isn't set up, the setup page shows these steps for exactly what's missing, plus a **Check again** button. After saving `.env`, click **Check again**; there's no need to restart the app.

**Adding a line to `.env`:**
1. Open the file named **.env** in the app folder. **Windows:** right-click it → **Open with** → **Notepad**. **Mac:** press **Cmd+Shift+.** to show hidden files, then open it with **TextEdit**. If there's no `.env`, copy **.env.example** and rename the copy to **.env**.
2. Add the line(s) below, with no spaces or quotes around the value.
3. Save, then click **Check again** on the setup page.

| Option | Get a key | Lines to add to `.env` |
|---|---|---|
| OpenAI voice | [platform.openai.com/api-keys](https://platform.openai.com/api-keys), and add credit under Billing | `OPENAI_API_KEY=sk-...` |
| ElevenLabs voice | [elevenlabs.io → API keys](https://elevenlabs.io/app/settings/api-keys) | `ELEVENLABS_API_KEY=...` |
| Deepgram voice | [console.deepgram.com](https://console.deepgram.com/) | `DEEPGRAM_API_KEY=...` |
| Simli face | [app.simli.com](https://app.simli.com/) | `SIMLI_API_KEY=...` and optionally `SIMLI_FACE_ID=...` (a preset face is used if blank) |
| D-ID face | [studio.d-id.com → account settings](https://studio.d-id.com/account-settings) | `DID_API_KEY=...`, `DID_SOURCE_URL=https://...` (a public link to a photo of the face), and optionally `DID_VOICE_ID=...` (default `en-US-JennyNeural`) |
| Tavus face | [platform.tavus.io → API keys](https://platform.tavus.io/api-keys) | `TAVUS_API_KEY=...` and `TAVUS_FACE_ID=...` (a face or replica ID from your Tavus account) |
| HeyGen face | [app.heygen.com → Settings → API](https://app.heygen.com/settings?nav=API) | `HEYGEN_API_KEY=...` and optionally `HEYGEN_AVATAR_ID=...` |

The OpenAI key is the same one used for OpenAI's AI models (see [MODELS.md](MODELS.md)), so if you already added it, OpenAI voice is ready.

**Lifelike faces use paid minutes while they're connected.** The app ends the session when you click **End & grade** or close the tab. If the browser crashes, the provider ends it automatically after its idle timeout.

---

## What has been tested

| Part | Tested? |
|---|---|
| Text, Voice, and Voice + face modes (switching, starting, saving the choice with the interview) | Yes, through the server |
| The witness's mood labels (Claude Haiku) | Yes: e.g. friendly at the start, calm once the interviewer explained their role, evasive when confronted with a document |
| Setup checks and instructions for every paid option | Yes |
| Free browser voice and animated face in an actual browser | **No.** The code was checked for errors, but it hasn't been run in a browser yet. |
| OpenAI, ElevenLabs, Deepgram voices | **No.** Built from each provider's documentation; needs a key to test. |
| Simli, D-ID, Tavus, HeyGen faces | **No.** Built from documentation (HeyGen from older documentation); needs paid accounts to test. Expect some of these to need fixes on first use. |

If a paid option fails, the error message from the provider appears on screen; send it along and it can be fixed.

---

## Troubleshooting

| What you see | What to do |
|---|---|
| **This browser can't recognize speech** | Use Chrome or Edge, or choose a paid voice service. |
| Clicking **Talk** does nothing, or says microphone access was blocked | Click the camera/microphone icon in the browser's address bar, choose **Allow**, and try again. |
| The witness's answers appear but you hear nothing | Check your sound. Make sure you clicked **Start the conversation**: browsers block sound until you click something on the page. |
| **Hear it** is silent with the browser voice | Some browsers load voices slowly. Wait a few seconds and try again, or choose another voice. |
| A lifelike face shows **Couldn't start: …** | Read the message. It's usually a wrong key or ID in `.env`, or no paid minutes left. |
| The face video freezes | Click **End & grade** to close the session cleanly, then start a new interview. |

---

## For developers

- **`media.json`:** the options shown on the setup page (names, prices, notes, key and setting names, voice lists, model IDs).
- **`media.py`:** the server half.
  - Status checks.
  - `transcribe()`: OpenAI `gpt-transcribe`, ElevenLabs `scribe_v2`, Deepgram `nova-3`.
  - `synthesize()`: OpenAI `gpt-4o-mini-tts`, ElevenLabs `eleven_v4_turbo`, Deepgram `aura-2-*`. It returns mp3, or 16 kHz PCM16 for Simli; OpenAI's 24 kHz PCM is resampled.
  - Avatar session start and stop, and the D-ID WebRTC relay. Uses plain `urllib`, so there are no new packages.
- **Endpoints:**
  - `GET /media`
  - `GET /media/voices?provider=`
  - `POST /speech/transcribe?provider=` (raw audio body)
  - `POST /speech/synthesize`
  - `POST /avatar/{provider}/start`
  - `POST /avatar/did/{sdp|ice|speak|stop}`
  - `POST /avatar/{provider}/stop`

  `POST /session/create` accepts `media: {mode, voice, voice_id, face}` and refuses anything not set up.
- **`static/media.js`:** the browser half.
  - The setup section.
  - Listening: `SpeechRecognition` for the browser option, otherwise `MediaRecorder` audio sent to the server.
  - Speaking: `speechSynthesis` for the browser option, otherwise mp3 from the server.
  - The SVG face, with its mouth driven by an audio analyser.
  - The avatar clients, loaded from CDNs only when chosen: `simli-client` and `@heygen/streaming-avatar` via esm.sh, and `@daily-co/daily-js` via unpkg for Tavus.
- **Mood tags:** in face mode, `agents.expert_reply` asks the witness to start each reply with `[mood]`. `agents.split_mood` removes the tag, and the transcript entry stores `mood`.
