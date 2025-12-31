# NoteIt Application Launcher
Write-Host "Starting NoteIt Application..." -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python is not found in PATH." -ForegroundColor Red
    Write-Host "Please install Python 3.8+ and add it to PATH." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Create .env if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item .env.example .env
        Write-Host "Warning: .env created from .env.example. Please ensure SECRET_KEY is set to a random value!" -ForegroundColor Yellow
        Write-Host "Generate a new SECRET_KEY with: python -c \"import secrets; print(secrets.token_hex(32))\"" -ForegroundColor Yellow
    } else {
        Write-Host "Generating random SECRET_KEY..." -ForegroundColor Yellow
        $secretKey = python -c "import secrets; print(secrets.token_hex(32))"
        @"
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=$secretKey
DATABASE_URL=sqlite:///noteit.db
"@ | Out-File -FilePath .env -Encoding utf8
        Write-Host ".env file created with a random SECRET_KEY" -ForegroundColor Green
    }
}

# Run the application
Write-Host ""
Write-Host "Starting NoteIt on http://localhost:5000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""
python app.py

