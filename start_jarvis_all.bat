
@echo off
cd /d "C:\Users\vandi\OneDrive\Desktop\hackathon\AI hackathon project"

if not exist logs mkdir logs

REM Start backend in the background
start "JARVIS Backend" /min cmd /c ".venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 >> logs\background.log 2>&1"

REM Start frontend in the background
start "JARVIS Frontend" /min cmd /c ".venv\Scripts\python.exe -m http.server 5500 --directory frontend --bind 127.0.0.1 >> logs\frontend.log 2>&1"
