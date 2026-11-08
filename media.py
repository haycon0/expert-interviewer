"""Voice and face services: speech-to-text, text-to-speech, and lifelike avatar sessions.

Options are listed in media.json. All calls are plain HTTPS requests from this
server, so API keys never reach the browser. The free options (the browser's own
speech and the animated face) need nothing here: they run entirely in the page.

API details follow each provider's documentation as checked on the date in
media.json; the paid services couldn't be tested without accounts.
"""

import json
import os
import urllib.error
import urllib.parse
import urllib.request
import uuid
from array import array
from pathlib import Path

import model_catalog

MEDIA_FILE = Path(__file__).parent / "media.json"
TIMEOUT = 60


class MediaError(Exception):
    """A voice or face service call failed; the message is safe to show the user."""


def load() -> dict:
    return json.loads(MEDIA_FILE.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# Setup status
# --------------------------------------------------------------------------

def _setting(name: str, spec: dict) -> str:
    return os.getenv(name, "").strip() or spec.get("default", "")


def status(kind: str, provider_id: str, catalog: dict | None = None) -> dict:
    """Whether a voice or face option is ready, and what's missing if not."""
    catalog = catalog or load()
    p = catalog[kind].get(provider_id)
    if p is None:
        return {"ready": False, "problems": [{"type": "unknown"}]}
    problems = []
    if p.get("key_env") and not os.getenv(p["key_env"], "").strip():
        problems.append({"type": "key", "key_env": p["key_env"]})
    for name, spec in p.get("settings", {}).items():
        if spec.get("required") and not _setting(name, spec):
            problems.append({"type": "setting", "name": name, "label": spec["label"]})
    return {"ready": not problems, "problems": problems}


def catalog_with_status() -> dict:
    model_catalog.reload_env()
    catalog = load()
    for kind in ("voice", "face"):
        for pid, p in catalog[kind].items():
            p["status"] = status(kind, pid, catalog)
    return catalog


# --------------------------------------------------------------------------
# HTTP helpers
# --------------------------------------------------------------------------

def _request(method: str, url: str, headers: dict, body: bytes | None = None,
             provider: str = "") -> bytes:
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:300]
        raise MediaError(f"{provider or url} returned an error ({e.code}): {detail}") from None
    except urllib.error.URLError as e:
        raise MediaError(f"Couldn't reach {provider or url}: {e.reason}") from None


def _json(method: str, url: str, headers: dict, payload: dict | None = None, provider: str = "") -> dict:
    body = json.dumps(payload).encode() if payload is not None else None
    raw = _request(method, url, {"Content-Type": "application/json", **headers}, body, provider)
    return json.loads(raw) if raw.strip() else {}


def _multipart(fields: dict, file_field: str, filename: str, data: bytes, mime: str) -> tuple[bytes, str]:
    boundary = uuid.uuid4().hex
    parts = []
    for k, v in fields.items():
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{file_field}"; '
                 f'filename="{filename}"\r\nContent-Type: {mime}\r\n\r\n'.encode())
    parts.append(data + b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def _key(provider_id: str, kind: str = "voice") -> str:
    p = load()[kind][provider_id]
    key = os.getenv(p["key_env"], "").strip()
    if not key:
        raise MediaError(f"{p['key_env']} isn't set in .env.")
    return key


def _ext(mime: str) -> str:
    return {"audio/webm": "webm", "audio/ogg": "ogg", "audio/mp4": "mp4", "audio/mpeg": "mp3",
            "audio/wav": "wav", "audio/x-wav": "wav"}.get(mime.split(";")[0].strip(), "webm")


# --------------------------------------------------------------------------
# Speech to text (hearing the interviewer)
# --------------------------------------------------------------------------

def transcribe(provider_id: str, audio: bytes, mime: str) -> str:
    model_catalog.reload_env()
    p = load()["voice"][provider_id]
    mime = mime or "audio/webm"
    if provider_id == "openai":
        body, ctype = _multipart({"model": p["stt_model"]}, "file", f"speech.{_ext(mime)}", audio, mime)
        out = json.loads(_request("POST", "https://api.openai.com/v1/audio/transcriptions",
                                  {"Authorization": f"Bearer {_key('openai')}", "Content-Type": ctype},
                                  body, "OpenAI"))
        return out.get("text", "").strip()
    if provider_id == "elevenlabs":
        body, ctype = _multipart({"model_id": p["stt_model"]}, "file", f"speech.{_ext(mime)}", audio, mime)
        out = json.loads(_request("POST", "https://api.elevenlabs.io/v1/speech-to-text",
                                  {"xi-api-key": _key("elevenlabs"), "Content-Type": ctype},
                                  body, "ElevenLabs"))
        return out.get("text", "").strip()
    if provider_id == "deepgram":
        q = urllib.parse.urlencode({"model": p["stt_model"], "smart_format": "true"})
        out = json.loads(_request("POST", f"https://api.deepgram.com/v1/listen?{q}",
                                  {"Authorization": f"Token {_key('deepgram')}",
                                   "Content-Type": mime.split(";")[0]}, audio, "Deepgram"))
        try:
            return out["results"]["channels"][0]["alternatives"][0]["transcript"].strip()
        except (KeyError, IndexError):
            return ""
    raise MediaError(f"{provider_id} can't transcribe speech on the server.")


# --------------------------------------------------------------------------
# Text to speech (the witness's voice)
# --------------------------------------------------------------------------

def _resample_pcm16(pcm: bytes, src_rate: int, dst_rate: int) -> bytes:
    """Linear resampling of mono 16-bit PCM (e.g. OpenAI's 24 kHz to Simli's 16 kHz)."""
    samples = array("h")
    samples.frombytes(pcm[: len(pcm) - len(pcm) % 2])
    if not samples or src_rate == dst_rate:
        return samples.tobytes()
    n = int(len(samples) * dst_rate / src_rate)
    out = array("h", bytes(2 * n))
    step = src_rate / dst_rate
    for i in range(n):
        x = i * step
        j = int(x)
        frac = x - j
        a = samples[j]
        b = samples[j + 1] if j + 1 < len(samples) else a
        out[i] = int(a + (b - a) * frac)
    return out.tobytes()


def synthesize(provider_id: str, text: str, voice: str = "", fmt: str = "mp3") -> tuple[bytes, str]:
    """Speak text. fmt "mp3" for playback, or "pcm16" (raw 16 kHz mono) for lip-sync avatars."""
    model_catalog.reload_env()
    p = load()["voice"][provider_id]
    voice = voice or p.get("default_voice", "")
    pcm = fmt == "pcm16"
    if provider_id == "openai":
        audio = _request("POST", "https://api.openai.com/v1/audio/speech",
                         {"Authorization": f"Bearer {_key('openai')}", "Content-Type": "application/json"},
                         json.dumps({"model": p["tts_model"], "input": text, "voice": voice,
                                     "response_format": "pcm" if pcm else "mp3"}).encode(), "OpenAI")
        # OpenAI's raw PCM is 24 kHz.
        return (_resample_pcm16(audio, 24000, 16000), "audio/pcm") if pcm else (audio, "audio/mpeg")
    if provider_id == "elevenlabs":
        q = urllib.parse.urlencode({"output_format": "pcm_16000" if pcm else "mp3_44100_128"})
        audio = _request("POST", f"https://api.elevenlabs.io/v1/text-to-speech/{urllib.parse.quote(voice)}?{q}",
                         {"xi-api-key": _key("elevenlabs"), "Content-Type": "application/json"},
                         json.dumps({"text": text, "model_id": p["tts_model"]}).encode(), "ElevenLabs")
        return audio, "audio/pcm" if pcm else "audio/mpeg"
    if provider_id == "deepgram":
        params = {"model": voice, "encoding": "linear16", "sample_rate": "16000", "container": "none"} \
            if pcm else {"model": voice, "encoding": "mp3"}
        audio = _request("POST", f"https://api.deepgram.com/v1/speak?{urllib.parse.urlencode(params)}",
                         {"Authorization": f"Token {_key('deepgram')}", "Content-Type": "application/json"},
                         json.dumps({"text": text}).encode(), "Deepgram")
        return audio, "audio/pcm" if pcm else "audio/mpeg"
    raise MediaError(f"{provider_id} can't speak on the server.")


def voices(provider_id: str) -> list[dict]:
    """Voices to choose from: [{id, name}]. ElevenLabs voices come from the user's account."""
    model_catalog.reload_env()
    p = load()["voice"][provider_id]
    if provider_id == "elevenlabs":
        try:
            out = _json("GET", "https://api.elevenlabs.io/v2/voices?page_size=100",
                        {"xi-api-key": _key("elevenlabs")}, provider="ElevenLabs")
            found = [{"id": v["voice_id"], "name": v.get("name") or v["voice_id"]} for v in out.get("voices", [])]
            if found:
                return found
        except MediaError:
            pass
    ids = p.get("voices") or ([p["default_voice"]] if p.get("default_voice") else [])
    return [{"id": v, "name": v} for v in ids]


# --------------------------------------------------------------------------
# Lifelike avatars (server half: creating and ending sessions)
# --------------------------------------------------------------------------

def _face_setting(provider_id: str, name: str) -> str:
    spec = load()["face"][provider_id].get("settings", {}).get(name, {})
    return _setting(name, spec)


def avatar_start(provider_id: str) -> dict:
    """Create an avatar session. Returns whatever the browser needs to connect."""
    model_catalog.reload_env()
    if provider_id == "simli":
        out = _json("POST", "https://api.simli.ai/compose/token",
                    {"x-simli-api-key": _key("simli", "face")},
                    {"faceId": _face_setting("simli", "SIMLI_FACE_ID"), "apiVersion": "v2",
                     "handleSilence": True, "maxSessionLength": 3600, "maxIdleTime": 300},
                    "Simli")
        return {"session_token": out["session_token"]}
    if provider_id == "did":
        out = _json("POST", "https://api.d-id.com/talks/streams",
                    {"Authorization": f"Basic {_key('did', 'face')}"},
                    {"source_url": _face_setting("did", "DID_SOURCE_URL")}, "D-ID")
        return {"id": out["id"], "session_id": out.get("session_id"),
                "offer": out.get("offer") or out.get("jsep"), "ice_servers": out.get("ice_servers", [])}
    if provider_id == "tavus":
        face = _face_setting("tavus", "TAVUS_FACE_ID")
        out = _json("POST", "https://tavusapi.com/v2/conversations",
                    {"x-api-key": _key("tavus", "face")},
                    {"face_id": face, "conversation_name": "Expert Interviewer witness",
                     "properties": {"max_call_duration": 3600}}, "Tavus")
        return {"conversation_id": out["conversation_id"], "conversation_url": out["conversation_url"]}
    if provider_id == "heygen":
        out = _json("POST", "https://api.heygen.com/v1/streaming.create_token",
                    {"x-api-key": _key("heygen", "face")}, {}, "HeyGen")
        return {"token": (out.get("data") or {}).get("token"),
                "avatar_id": _face_setting("heygen", "HEYGEN_AVATAR_ID")}
    raise MediaError(f"{provider_id} isn't a lifelike avatar option.")


def did_call(action: str, stream_id: str, payload: dict) -> dict:
    """D-ID's WebRTC handshake and speech, relayed so the key stays on the server."""
    auth = {"Authorization": f"Basic {_key('did', 'face')}"}
    base = f"https://api.d-id.com/talks/streams/{urllib.parse.quote(stream_id)}"
    if action == "sdp":
        return _json("POST", f"{base}/sdp", auth,
                     {"answer": payload["answer"], "session_id": payload["session_id"]}, "D-ID")
    if action == "ice":
        return _json("POST", f"{base}/ice", auth,
                     {k: payload.get(k) for k in ("candidate", "sdpMid", "sdpMLineIndex", "session_id")}, "D-ID")
    if action == "speak":
        voice = _face_setting("did", "DID_VOICE_ID")
        return _json("POST", base, auth, {
            "session_id": payload["session_id"],
            "script": {"type": "text", "input": payload["text"],
                       "provider": {"type": "microsoft", "voice_id": voice}},
        }, "D-ID")
    if action == "stop":
        return _json("DELETE", base, auth, {"session_id": payload["session_id"]}, "D-ID")
    raise MediaError(f"Unknown D-ID action {action}.")


def avatar_stop(provider_id: str, payload: dict) -> None:
    """End a session so it stops using paid minutes. Errors are ignored: the session
    also times out on the provider's side."""
    try:
        if provider_id == "tavus" and payload.get("conversation_id"):
            _request("POST", f"https://tavusapi.com/v2/conversations/"
                             f"{urllib.parse.quote(payload['conversation_id'])}/end",
                     {"x-api-key": _key("tavus", "face")}, b"", "Tavus")
        elif provider_id == "did" and payload.get("id"):
            did_call("stop", payload["id"], payload)
    except MediaError:
        pass

