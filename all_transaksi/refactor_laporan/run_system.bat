@echo off
echo ====================================================
echo FFB Analysis System - Starting Application
echo ====================================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please run setup.bat first to install dependencies
    pause
    exit /b 1
)

:: Check if main.py exists
if not exist "main.py" (
    echo ERROR: main.py not found
    echo Please run this script from the refactor_laporan directory
    pause
    exit /b 1
)

:: Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

:: Start the application
echo Starting FFB Analysis System...
echo.
python main.py

:: If application crashes, show error
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Application failed to start
    echo Error code: %errorlevel%
    echo.
    echo Troubleshooting:
    echo 1. Make sure all dependencies are installed (run setup.bat)
    echo 2. Check database connections: python main.py --test-connections
    echo 3. See logs folder for detailed error messages
    echo.
    pause
)

echo.
echo Application closed.
pause