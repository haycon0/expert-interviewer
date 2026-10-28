#!/bin/bash
# Double-click this file (Mac) to set up (first time) and start Expert Interviewer.
cd "$(dirname "$0")" || exit 1

if ! command -v python3 >/dev/null 2>&1; then
  echo
  echo "Python is not installed. Install it from https://www.python.org/downloads/"
  echo "then double-click this file again."
  read -r -p "Press Enter to close."
  exit 1
fi

if [ ! -x .venv/bin/python ]; then
  echo "First-time setup: installing what the app needs. This takes 1-3 minutes..."
  python3 -m venv .venv || { read -r -p "Setup failed. Press Enter to close."; exit 1; }
fi
PY=.venv/bin/python
"$PY" -m pip install --quiet --disable-pip-version-check -r requirements.txt \
  || { echo "Setup failed. Check your internet connection and try again."; read -r -p "Press Enter to close."; exit 1; }

if ! grep -q '^ANTHROPIC_API_KEY=sk-' .env 2>/dev/null; then
  echo
  echo "No API key found yet."
  echo "Paste your Anthropic API key below and press Enter (Cmd+V to paste)."
  echo "Or just press Enter to try the app in demo mode with canned answers."
  read -r -p "API key: " KEY
  if [ -n "$KEY" ]; then
    printf 'ANTHROPIC_API_KEY=%s\nMODEL=anthropic:claude-sonnet-5-5\n' "$KEY" > .env
    echo "Key saved."
  fi
fi

echo
echo "Starting Expert Interviewer..."
echo "Your browser will open in a few seconds at http://127.0.0.1:8000"
echo "KEEP THIS WINDOW OPEN while you use the app. Close it when you're done."
echo
[ -z "$NO_BROWSER" ] && (sleep 5; open http://127.0.0.1:8000) &
"$PY" -m uvicorn server:app --port 8000
