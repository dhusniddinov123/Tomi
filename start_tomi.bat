@echo off
REM Tomi AI Assistant - Windows Startup Script

echo Starting Tomi AI Assistant...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if Ollama is running
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo Warning: Ollama service may not be running
    echo Please start Ollama first: ollama serve
    timeout /t 5
)

REM Change to Tomi directory
cd /d %~dp0

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Run Tomi
python main.py

pause
