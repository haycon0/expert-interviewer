@echo off
REM Double-click this file to set up (first time) and start Expert Interviewer.
cd /d "%~dp0"
title Expert Interviewer

python --version >nul 2>&1
if errorlevel 1 (
  echo.
  echo Python is not installed, or Windows can't find it.
  echo Install it from https://www.python.org/downloads/ and tick
  echo "Add python.exe to PATH" on the first screen of the installer.
  echo Then double-click this file again.
  echo.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo First-time setup: installing what the app needs. This takes 1-3 minutes...
  python -m venv .venv
  if errorlevel 1 goto :setupfailed
)
set "PY=.venv\Scripts\python.exe"
"%PY%" -m pip install --quiet --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto :setupfailed

findstr /b /c:"ANTHROPIC_API_KEY=sk-" .env >nul 2>&1
if errorlevel 1 (
  echo.
  echo No API key found yet.
  echo Paste your Anthropic API key below and press Enter
  echo ^(right-click in this window to paste^).
  echo Or just press Enter to try the app in demo mode with canned answers.
  echo.
  set "KEY="
  set /p "KEY=API key: "
  call :savekey
)

echo.
echo Starting Expert Interviewer...
echo Your browser will open in a few seconds at http://127.0.0.1:8000
echo KEEP THIS WINDOW OPEN while you use the app. Close it when you're done.
echo.
if not defined NO_BROWSER start "" cmd /c "timeout /t 5 >nul & start http://127.0.0.1:8000"
"%PY%" -m uvicorn server:app --port 8000
echo.
echo The app has stopped.
pause
exit /b 0

:savekey
if not defined KEY exit /b 0
> .env echo ANTHROPIC_API_KEY=%KEY%
>> .env echo MODEL=anthropic:claude-sonnet-5-5
echo Key saved.
exit /b 0

:setupfailed
echo.
echo Setup failed. Check your internet connection and try again.
echo If it keeps failing, see the Troubleshooting section in SETUP.md.
pause
exit /b 1
