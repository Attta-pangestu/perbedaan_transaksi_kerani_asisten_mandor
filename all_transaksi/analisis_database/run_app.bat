@echo off
REM FFB Analysis System v2.0 - Application Launcher
REM This script launches the FFB Analysis System with proper environment

echo ========================================
echo FFB Analysis System v2.0 - Launcher
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    echo.
    pause
    exit /b 1
)

echo Python found. Launching FFB Analysis System...
echo.

REM Run the application launcher
python run_application.py

REM Check the result
if errorlevel 1 (
    echo.
    echo Application encountered an error
    echo Please review the error messages above
) else (
    echo.
    echo Application closed normally
)

echo.
pause