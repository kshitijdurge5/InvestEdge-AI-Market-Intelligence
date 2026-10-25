@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%.."
set "PY=%BACKEND_DIR%\.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"
echo Installing/upgrading official Upstox Python SDK...
"%PY%" -m pip install --upgrade upstox-python-sdk
if errorlevel 1 (
  echo SDK installation failed.
  pause
  exit /b 1
)
echo Starting InvestEdge live-stream test...
"%PY%" "%SCRIPT_DIR%run_market_stream_test.py"
pause
