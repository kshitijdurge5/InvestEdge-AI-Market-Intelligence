@echo off
setlocal
cd /d "%~dp0website"
where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found on PATH. Install Python 3.11 or use the Python launcher.
  pause
  exit /b 1
)
start "" http://localhost:8091
python -m http.server 8091
pause
