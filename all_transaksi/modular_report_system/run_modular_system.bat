@echo off
echo Starting Modular Report System...
echo.

REM Change to the modular report system directory
cd /d "%~dp0modular_report_system"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking dependencies...
python -c "import tkinter, pandas, reportlab, openpyxl" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install pandas reportlab openpyxl
    if errorlevel 1 (
        echo Error: Failed to install required packages
        pause
        exit /b 1
    )
)

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Run the application
echo.
echo Launching Modular Report System GUI...
python main.py

REM Check if the application ran successfully
if errorlevel 1 (
    echo.
    echo Application encountered an error. Check logs for details.
    pause
) else (
    echo.
    echo Application closed successfully.
)

pause