
@echo off
cd /d "C:\Users\vandi\OneDrive\Desktop\hackathon\AI hackathon project"

if not exist logs mkdir logs

echo Starting JARVIS backend... >> "logs\background.log"

".venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 >> "logs\background.log" 2>&1
