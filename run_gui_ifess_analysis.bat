@echo off
echo ===============================================
echo      IFESS DATABASE ANALYSIS TOOL - GUI
echo ===============================================
echo.

set PYTHON_CMD=python
set SCRIPT_DIR=%~dp0

echo Script directory: %SCRIPT_DIR%
echo.

:: Check if Python is available
%PYTHON_CMD% --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python tidak ditemukan. Pastikan Python sudah terinstall dan ada di PATH.
    pause
    exit /b 1
)

:: Check if GUI script exists
if not exist "%SCRIPT_DIR%gui_ifess_analysis.py" (
    echo ERROR: File gui_ifess_analysis.py tidak ditemukan di direktori ini.
    pause
    exit /b 1
)

:: Check dependencies
echo Checking Python dependencies...
%PYTHON_CMD% -c "import tkinter, pandas, json" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Dependencies tidak lengkap. Install dependencies dengan:
    echo pip install pandas openpyxl
    echo.
    echo Tkinter sudah termasuk dalam Python standard library.
    pause
    exit /b 1
)

echo ✓ Dependencies OK
echo.

echo Menjalankan Ifess Database Analysis Tool GUI...
echo.

%PYTHON_CMD% "%SCRIPT_DIR%gui_ifess_analysis.py"

if errorlevel 1 (
    echo.
    echo Error saat menjalankan aplikasi!
    pause
) else (
    echo.
    echo Aplikasi selesai.
) 