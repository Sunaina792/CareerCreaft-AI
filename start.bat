@echo off
echo =======================================
echo   CareerCraft AI - Starting Server
echo =======================================
cd /d "%~dp0"
echo.
echo Add your GROQ_API_KEY to backend\.env before running!
echo.
C:\Users\4suna\.local\bin\uv.exe run uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
pause
