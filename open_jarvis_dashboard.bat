
@echo off
setlocal

echo Waiting for JARVIS backend and frontend...

:wait_for_servers
powershell -NoProfile -ExecutionPolicy Bypass -Command "$b = Test-NetConnection 127.0.0.1 -Port 8000 -InformationLevel Quiet; $f = Test-NetConnection 127.0.0.1 -Port 5500 -InformationLevel Quiet; if ($b -and $f) { exit 0 } else { exit 1 }" >nul 2>&1

if errorlevel 1 (
    timeout /t 2 /nobreak >nul
    goto wait_for_servers
)

start "" "http://127.0.0.1:5500/claude%%20index.html"
exit
