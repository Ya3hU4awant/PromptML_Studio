# PromptML Studio - Quick Setup Script
# This script sets up the environment and runs the application

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PromptML Studio - Quick Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "  $pythonVersion" -ForegroundColor Green

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found! Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "  Virtual environment already exists" -ForegroundColor Green
} else {
    python -m venv venv
    Write-Host "  Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host ""
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies (this may take 5-10 minutes)..." -ForegroundColor Yellow
Write-Host "  Please be patient..." -ForegroundColor Cyan

pip install -r requirements.txt --quiet

if ($LASTEXITCODE -eq 0) {
    Write-Host "  Dependencies installed successfully!" -ForegroundColor Green
} else {
    Write-Host "  WARNING: Some dependencies may have failed to install" -ForegroundColor Yellow
}

# Display success message
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Run the app: streamlit run app.py" -ForegroundColor White
Write-Host "  2. Open browser: http://localhost:8501" -ForegroundColor White
Write-Host "  3. Test components: python test_components.py" -ForegroundColor White
Write-Host ""
Write-Host "Would you like to start the app now? (Y/N)" -ForegroundColor Yellow
$response = Read-Host

if ($response -eq 'Y' -or $response -eq 'y') {
    Write-Host ""
    Write-Host "Starting PromptML Studio..." -ForegroundColor Cyan
    Write-Host "  App will open at: http://localhost:8501" -ForegroundColor Green
    Write-Host "  Press Ctrl+C to stop" -ForegroundColor Yellow
    Write-Host ""
    streamlit run app.py
} else {
    Write-Host ""
    Write-Host "Setup complete! Run 'streamlit run app.py' when ready." -ForegroundColor Green
    Write-Host ""
}
