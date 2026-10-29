
@echo off
cd /d "%~dp0"

if not exist "logs" mkdir "logs"

".venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 >> "logs\backend.log" 2>&1