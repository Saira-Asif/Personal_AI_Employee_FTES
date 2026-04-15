@echo off
REM AI Employee Setup Script for Windows
REM Run this to install dependencies and validate Bronze Tier

echo ================================================
echo AI Employee Watchers - Windows Setup
echo ================================================

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.13+ from:
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo Python found. Installing dependencies...

REM Install dependencies
cd watchers
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Dependencies installed. Running validation...
echo.

REM Run validation
python setup.py --test
if errorlevel 1 (
    echo.
    echo WARNING: Some validation checks failed.
    echo Review the output above.
) else (
    echo.
    echo Setup complete! Bronze Tier is ready.
    echo.
    echo Next steps:
    echo   1. Open AI_Employee_Vault in Obsidian
    echo   2. Run: python orchestrator.py ..\AI_Employee_Vault
    echo   3. Drop files into AI_Employee_Vault\Inbox\
)

cd ..
echo.
pause
