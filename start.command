#!/bin/bash
# Double-click this file (Mac) to set up (first time) and start Expert Interviewer.
cd "$(dirname "$0")" || exit 1

# The app's Python packages live outside this folder, because folders synced by
# iCloud Drive (e.g. Desktop and Documents) make installs slow and can corrupt them.
ENVDIR="$HOME/Library/Application Support/ExpertInterviewer/env"
PY="$ENVDIR/bin/python"
MARKER="$ENVDIR/installed-requirements.txt"

echo "Checking for Python..."
if ! command -v python3 >/dev/null 2>&1; then
  echo
  echo "Python is not installed. Install it from https://www.python.org/downloads/"
  echo "then double-click this file again."
  read -r -p "Press Enter to close."
  exit 1
fi

# Reinstall if there's no finished install, or requirements.txt has changed.
# (The marker file is only written after an install completes successfully.)
if ! cmp -s requirements.txt "$MARKER"; then
  echo
  echo "Installing what the app needs. This takes 2-5 minutes the first time,"
  echo "and you'll see progress below. Please don't close this window."
  echo
  rm -rf "$ENVDIR"
  if python3 -m venv "$ENVDIR" && "$PY" -m pip install --disable-pip-version-check -r requirements.txt; then
    cp requirements.txt "$MARKER"
    echo
    echo "Install complete."
  else
    echo
    echo "Setup failed. Check your internet connection and open start.command again."
    read -r -p "Press Enter to close."
    exit 1
  fi
fi

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
echo "Starting Expert Interviewer. This takes about 10-30 seconds..."
echo "Your browser will open automatically when it's ready."
echo "KEEP THIS WINDOW OPEN while you use the app. Close it when you're done."
echo
[ -z "$NO_BROWSER" ] && export OPEN_BROWSER=1
if ! "$PY" -m uvicorn server:app --port 8000; then
  # Force a clean reinstall next time in case the install was damaged.
  rm -f "$MARKER"
  echo
  echo "The app stopped because of an error (see above)."
  echo "Open start.command again to repair it. It will reinstall, which takes 2-5 minutes."
  echo "If the error says 'address already in use', the app is already open in another window."
  read -r -p "Press Enter to close."
fi
