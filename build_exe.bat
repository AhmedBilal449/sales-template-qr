@echo off
echo ========================================
echo   CSV Template Generator - Build Script
echo ========================================
echo.

REM Check if virtual environment is activated
if not defined VIRTUAL_ENV (
    echo Activating virtual environment...
    call env\Scripts\activate.bat
    if errorlevel 1 (
        echo ERROR: Failed to activate virtual environment
        echo Please make sure the 'env' folder exists and contains a valid Python virtual environment
        pause
        exit /b 1
    )
)

echo Virtual environment activated: %VIRTUAL_ENV%
echo.

REM Install/upgrade PyInstaller if needed
echo Installing/upgrading PyInstaller...
pip install --upgrade pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    pause
    exit /b 1
)

echo.
echo Building executable...
echo This may take several minutes...
echo.

REM Clean previous builds
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Build the executable using the spec file
pyinstaller --clean app.spec
if errorlevel 1 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo           BUILD COMPLETED!
echo ========================================
echo.
echo The executable has been created in the 'dist' folder.
echo You can find it at: dist\CSV_Template_Generator\CSV_Template_Generator.exe
echo.
echo To distribute the application:
echo 1. Copy the entire 'dist\CSV_Template_Generator' folder
echo 2. The folder contains all necessary files to run on other computers
echo 3. Run CSV_Template_Generator.exe to start the application
echo.

REM Open the dist folder
if exist "dist\CSV_Template_Generator" (
    echo Opening the distribution folder...
    explorer "dist\CSV_Template_Generator"
)

echo.
echo Press any key to exit...
pause >nul
