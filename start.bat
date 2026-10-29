@echo off
REM Double-click this file to set up (first time) and start Expert Interviewer.
cd /d "%~dp0"
title Expert Interviewer

REM The app's Python packages live outside this folder (in your local AppData),
REM because folders synced by OneDrive make installs slow and can corrupt them.
set "ENVDIR=%LOCALAPPDATA%\ExpertInterviewer\env"
set "PY=%ENVDIR%\Scripts\python.exe"
set "MARKER=%ENVDIR%\installed-requirements.txt"

echo Checking for Python...
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

REM Reinstall if there's no finished install, or requirements.txt has changed.
REM (The marker file is only written after an install completes successfully.)
fc /b requirements.txt "%MARKER%" >nul 2>&1
if errorlevel 1 call :install || goto :setupfailed

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
echo Starting Expert Interviewer. This takes about 10-30 seconds...
echo Your browser will open automatically when it's ready.
echo KEEP THIS WINDOW OPEN while you use the app. Close it when you're done.
echo.
if not defined NO_BROWSER set "OPEN_BROWSER=1"
"%PY%" -m uvicorn server:app --port 8000
if errorlevel 1 (
  REM Force a clean reinstall next time in case the install was damaged.
  del "%MARKER%" >nul 2>&1
  echo.
  echo The app stopped because of an error ^(see above^).
  echo Double-click start.bat again to repair it. It will reinstall, which takes 2-5 minutes.
  echo If the error says "address already in use", the app is already open in another window.
)
pause
exit /b 0

:install
echo.
echo Installing what the app needs. This takes 2-5 minutes the first time,
echo and you'll see progress below. Please don't close this window.
echo.
if exist "%ENVDIR%" rmdir /s /q "%ENVDIR%"
python -m venv "%ENVDIR%" || exit /b 1
"%PY%" -m pip install --disable-pip-version-check --progress-bar on -r requirements.txt || exit /b 1
copy /y requirements.txt "%MARKER%" >nul
echo.
echo Install complete.
exit /b 0

:savekey
if not defined KEY exit /b 0
> .env echo ANTHROPIC_API_KEY=%KEY%
>> .env echo MODEL=anthropic:claude-sonnet-5-5
echo Key saved.
exit /b 0

:setupfailed
echo.
echo Setup failed. Check your internet connection and double-click start.bat again.
echo If it keeps failing, see the troubleshooting section in SETUP.md.
pause
exit /b 1
