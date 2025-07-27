@echo off
echo ===============================================
echo    TESTING SETUP ANALISIS KINERJA KARYAWAN
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
if not exist "%SCRIPT_DIR%test_koneksi_karyawan.py" (
    echo ERROR: File test_koneksi_karyawan.py tidak ditemukan di direktori ini.
    pause
    exit /b 1
)

echo Menjalankan testing setup...
echo.

%PYTHON_CMD% "%SCRIPT_DIR%test_koneksi_karyawan.py"

echo.
echo Testing selesai! Periksa hasil di atas.
pause 