@echo off
setlocal
cd /d "%~dp0"
set "BACKEND_DIR=.."
set "PY=%BACKEND_DIR%\.venv\Scripts\python.exe"
if not exist "%PY%" set "PY=python"
echo Starting InvestEdge Live Gateway on http://127.0.0.1:8011
"%PY%" -m uvicorn live_gateway:app --host 127.0.0.1 --port 8011
pause
