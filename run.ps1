Set-Location $PSScriptRoot\backend

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example - please add your OPENAI_API_KEY" -ForegroundColor Yellow
    notepad .env
    Read-Host "Press Enter after saving your .env"
}

if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    py -3 -m venv venv
}

Write-Host "Activating venv and installing dependencies..." -ForegroundColor Cyan
& .\venv\Scripts\Activate.ps1
pip install -q -r requirements.txt

Write-Host "Starting Milya Scribe Plus on http://localhost:8000" -ForegroundColor Green
python -m uvicorn app.main:app --reload --port 8000
