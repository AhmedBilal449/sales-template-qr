# CSV Template Generator - PowerShell Build Script

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CSV Template Generator - Build Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "env\Scripts\Activate.ps1"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to activate virtual environment" -ForegroundColor Red
        Write-Host "Please make sure the 'env' folder exists and contains a valid Python virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host "Virtual environment activated: $env:VIRTUAL_ENV" -ForegroundColor Green
Write-Host ""

# Install/upgrade PyInstaller if needed
Write-Host "Installing/upgrading PyInstaller..." -ForegroundColor Yellow
pip install --upgrade pyinstaller
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install PyInstaller" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Building executable..." -ForegroundColor Yellow
Write-Host "This may take several minutes..." -ForegroundColor Yellow
Write-Host ""

# Clean previous builds
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }

# Build the executable using the spec file
pyinstaller --clean app.spec
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Build failed!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "           BUILD COMPLETED!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "The executable has been created in the 'dist' folder." -ForegroundColor Green
Write-Host "You can find it at: dist\CSV_Template_Generator\CSV_Template_Generator.exe" -ForegroundColor Green
Write-Host ""
Write-Host "To distribute the application:" -ForegroundColor Cyan
Write-Host "1. Copy the entire 'dist\CSV_Template_Generator' folder" -ForegroundColor White
Write-Host "2. The folder contains all necessary files to run on other computers" -ForegroundColor White
Write-Host "3. Run CSV_Template_Generator.exe to start the application" -ForegroundColor White
Write-Host ""

# Open the dist folder
if (Test-Path "dist\CSV_Template_Generator") {
    Write-Host "Opening the distribution folder..." -ForegroundColor Yellow
    Invoke-Item "dist\CSV_Template_Generator"
}

Write-Host ""
Read-Host "Press Enter to exit"
