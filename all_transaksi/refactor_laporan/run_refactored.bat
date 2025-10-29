@echo off
echo ===============================================================
echo    FFB ANALYSIS SYSTEM - REFACTORED VERSION
echo ===============================================================
echo.

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo Error: Python not found or not accessible
    echo Please install Python 3.8+ and add to PATH
    pause
    exit /b 1
)

echo Python found successfully
echo.

echo Checking dependencies...
python -c "import sys; print('Python path:', sys.executable); import tkinter; print('tkinter: OK')"

echo.
echo Starting FFB Analysis System (Refactored)...
echo ===============================================================

cd /d "%~dp0"

python main.py

if errorlevel 1 (
    echo.
    echo ===============================================================
    echo    ERROR: Application failed to start
    echo ===============================================================
    echo.
    echo Common solutions:
    echo    1. Check Python dependencies are installed
    echo    2. Verify all modules are in correct directories
    echo    3. Check file permissions
    echo    4. Run in debug mode: set DEBUG=1 && run_refactored.bat
    echo.
    pause
    exit /b 1
)

echo.
echo Application closed normally
pause