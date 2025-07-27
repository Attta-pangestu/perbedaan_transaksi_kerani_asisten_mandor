@echo off
echo FFB Scanner Analysis - Complete Test and Launch
echo ==============================================

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python tidak ditemukan
    echo Silakan install Python terlebih dahulu
    pause
    exit /b 1
)

echo Python ditemukan
echo.

echo Step 1: Testing GUI Logic...
echo ---------------------------
python test_corrected_gui.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Test failed! Please fix the issues before running the GUI.
    pause
    exit /b 1
)

echo.
echo ✅ All tests passed!
echo.
echo Step 2: Launching GUI...
echo ----------------------
python gui_ffb_analysis_corrected.py

echo.
echo GUI selesai
pause 