@echo off
REM FFB Analysis System v2.0 - Test Runner
REM This script runs all system validation tests

echo ========================================
echo FFB Analysis System v2.0 - Test Runner
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    echo.
    pause
    exit /b 1
)

echo Python found. Starting system validation...
echo.

REM Run the validation script
python test_system.py

REM Check the result
if errorlevel 1 (
    echo.
    echo Tests completed with errors or warnings
    echo Please review the output above for details
) else (
    echo.
    echo All tests passed successfully!
    echo System is ready for use
)

echo.
pause