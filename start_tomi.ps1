# Tomi AI Assistant - PowerShell Startup Script

Write-Host "Starting Tomi AI Assistant..." -ForegroundColor Cyan

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Ollama is running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "Ollama service is running" -ForegroundColor Green
} catch {
    Write-Host "Warning: Ollama service may not be running" -ForegroundColor Yellow
    Write-Host "Please start Ollama first: ollama serve" -ForegroundColor Yellow
    Start-Sleep -Seconds 3
}

# Change to Tomi directory
Set-Location $PSScriptRoot

# Activate virtual environment if it exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Cyan
    & "venv\Scripts\Activate.ps1"
}

# Run Tomi
Write-Host "Launching Tomi..." -ForegroundColor Cyan
python main.py

Read-Host "Press Enter to exit"
