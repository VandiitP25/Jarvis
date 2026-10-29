
@echo off
cd /d "C:\Users\vandi\OneDrive\Desktop\hackathon\AI hackathon project"

".venv\Scripts\python.exe" -m http.server 5500 --directory frontend --bind 127.0.0.1
