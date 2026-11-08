"""Access control for running the app on the internet: a shared password and usage limits.

All of it is off by default, so running on your own computer works as before.

- APP_PASSWORD: when set, every page and API call needs a login with this password.
  Logins last 7 days (a signed cookie); changing the password logs everyone out.
- MAX_INTERVIEWS_PER_DAY: caps new interviews per day (UTC) across all users.
- MAX_QUESTIONS_PER_INTERVIEW: caps the questions in one interview.
- When the app is detected running online (on Render, or with ALLOWED_HOSTS set)
  and APP_PASSWORD isn't set, it refuses to serve anything rather than run open.
"""

import hashlib
import hmac
import os
import time
from datetime import datetime, timezone
from urllib.parse import parse_qs

from fastapi import Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

COOKIE = "ei_login"
LOGIN_DAYS = 7
MAX_FAILURES, FAILURE_WINDOW = 10, 15 * 60   # per visitor: 10 wrong passwords per 15 minutes
OPEN_PATHS = {"/login", "/healthz"}


def password() -> str:
    return os.getenv("APP_PASSWORD", "").strip()


def online() -> bool:
    return bool(os.getenv("RENDER") or os.getenv("ALLOWED_HOSTS", "").strip())


def allowed_hosts() -> list[str]:
    hosts = ["localhost", "127.0.0.1", "[::1]", "testserver"]
    if h := os.getenv("RENDER_EXTERNAL_HOSTNAME", "").strip():
        hosts.append(h)
    hosts += [h.strip() for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()]
    return hosts


# --------------------------------------------------------------------------
# Signed login cookie
# --------------------------------------------------------------------------

def _key() -> bytes:
    # Derived from the password (plus an optional secret), so a new password
    # invalidates every existing login.
    return hashlib.sha256(f"{os.getenv('SESSION_SECRET', '')}|{password()}".encode()).digest()


def _sign(expires: int) -> str:
    return hmac.new(_key(), str(expires).encode(), hashlib.sha256).hexdigest()


def make_cookie() -> str:
    expires = int(time.time()) + LOGIN_DAYS * 86400
    return f"{expires}.{_sign(expires)}"


def valid_cookie(value: str | None) -> bool:
    try:
        expires_s, sig = (value or "").split(".", 1)
        expires = int(expires_s)
    except ValueError:
        return False
    return expires > time.time() and hmac.compare_digest(sig, _sign(expires))


# --------------------------------------------------------------------------
# Failed-login throttle
# --------------------------------------------------------------------------

_failures: dict[str, list[float]] = {}


def _client(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def _too_many(ip: str) -> bool:
    now = time.time()
    _failures[ip] = [t for t in _failures.get(ip, []) if now - t < FAILURE_WINDOW]
    return len(_failures[ip]) >= MAX_FAILURES


# --------------------------------------------------------------------------
# Login page and middleware
# --------------------------------------------------------------------------

LOGIN_PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Expert Interviewer: sign in</title>
<style>
 body{margin:0;font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif;background:#f6f5f2;color:#1d1d1f;display:flex;min-height:100vh;align-items:center;justify-content:center;padding:16px}
 form{background:#fff;border:1px solid #e3e1dc;border-radius:10px;padding:24px;width:100%;max-width:360px}
 h1{font-size:18px;margin:0 0 4px} p{color:#6b6b70;margin:0 0 16px;font-size:14px}
 input{width:100%;box-sizing:border-box;padding:9px 11px;border:1px solid #e3e1dc;border-radius:7px;font:inherit;margin-bottom:12px}
 button{background:#2f5d8a;color:#fff;border:0;border-radius:7px;padding:10px 18px;font:inherit;font-weight:600;cursor:pointer;width:100%}
 .err{color:#a8432f;font-size:14px;margin-bottom:10px}
</style></head><body>
<form method="post" action="/login">
 <h1>Expert Interviewer</h1><p>Enter the password you were given.</p>
 {error}
 <input type="password" name="password" placeholder="Password" autofocus required autocomplete="current-password">
 <button type="submit">Sign in</button>
</form></body></html>"""


def login_page(error: str = "") -> HTMLResponse:
    msg = f'<div class="err">{error}</div>' if error else ""
    return HTMLResponse(LOGIN_PAGE.replace("{error}", msg), status_code=401 if error else 200)


async def handle_login(request: Request):
    if request.method == "GET":
        return login_page()
    ip = _client(request)
    if _too_many(ip):
        return login_page("Too many wrong attempts. Wait 15 minutes and try again.")
    form = parse_qs((await request.body()).decode("utf-8", errors="replace"))
    given = (form.get("password") or [""])[0]
    if not password() or not hmac.compare_digest(given.encode(), password().encode()):
        _failures.setdefault(ip, []).append(time.time())
        return login_page("That password isn't right.")
    _failures.pop(ip, None)
    resp = RedirectResponse("/", status_code=303)
    resp.set_cookie(COOKIE, make_cookie(), max_age=LOGIN_DAYS * 86400, httponly=True,
                    samesite="lax", secure=request.url.scheme == "https")
    return resp


async def middleware(request: Request, call_next):
    path = request.url.path
    if path == "/healthz":
        return await call_next(request)
    if online() and not password():
        return HTMLResponse("This app is online without a password, so it's switched off. "
                            "Set APP_PASSWORD in the hosting service's environment settings.", status_code=503)
    if path == "/login":
        return await handle_login(request)
    if path == "/logout":
        resp = RedirectResponse("/login" if password() else "/", status_code=303)
        resp.delete_cookie(COOKIE)
        return resp
    if password() and not valid_cookie(request.cookies.get(COOKIE)):
        if request.method == "GET" and "text/html" in request.headers.get("accept", ""):
            return RedirectResponse("/login", status_code=303)
        return JSONResponse({"detail": "Please sign in again."}, status_code=401)
    return await call_next(request)


# --------------------------------------------------------------------------
# Usage limits
# --------------------------------------------------------------------------

_interviews: dict[str, int] = {}


def _limit(name: str) -> int:
    try:
        return max(0, int(os.getenv(name, "0").strip() or 0))
    except ValueError:
        return 0


def take_interview() -> str | None:
    """Count a new interview. Returns an error message if today's limit is reached."""
    limit = _limit("MAX_INTERVIEWS_PER_DAY")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for day in [d for d in _interviews if d != today]:
        del _interviews[day]
    if limit and _interviews.get(today, 0) >= limit:
        return (f"The daily limit of {limit} interviews has been reached. "
                "It resets at midnight UTC.")
    _interviews[today] = _interviews.get(today, 0) + 1
    return None


def question_limit_error(questions_so_far: int) -> str | None:
    limit = _limit("MAX_QUESTIONS_PER_INTERVIEW")
    if limit and questions_so_far >= limit:
        return f"This interview has reached the limit of {limit} questions. Click End & grade."
    return None
