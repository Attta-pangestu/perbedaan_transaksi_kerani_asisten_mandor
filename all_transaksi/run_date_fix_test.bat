@echo off
echo ===============================================
echo    IFESS ANALYSIS DATE FORMAT FIX TEST
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

:: Check if test script exists
if not exist "%SCRIPT_DIR%test_date_fix.py" (
    echo ERROR: File test_date_fix.py tidak ditemukan di direktori ini.
    pause
    exit /b 1
)

:: Check dependencies
echo Checking Python dependencies...
%PYTHON_CMD% -c "import pandas, sys, os, datetime" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Dependencies tidak lengkap. Install dependencies dengan:
    echo pip install pandas
    pause
    exit /b 1
)

echo ✓ Dependencies OK
echo.

echo Menjalankan test perbaikan format tanggal...
echo.

%PYTHON_CMD% "%SCRIPT_DIR%test_date_fix.py"

if errorlevel 1 (
    echo.
    echo Error saat menjalankan test!
    echo Silakan periksa error messages di atas.
    pause
) else (
    echo.
    echo Test selesai. Silakan periksa hasil di atas.
    pause
) 