@echo off
echo ===============================================
echo      ANALISIS KINERJA KARYAWAN FFB SCANNER
echo ===============================================
echo.

:: Set default values
set PYTHON_CMD=python
set SCRIPT_DIR=%~dp0
set OUTPUT_DIR=%SCRIPT_DIR%reports
set DB_PATH=D:\IFESS Firebird Database\MILL04.FDB

:: Create reports directory if it doesn't exist
if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

echo Script directory: %SCRIPT_DIR%
echo Output directory: %OUTPUT_DIR%
echo Database path: %DB_PATH%
echo.

:: Check if Python is available
%PYTHON_CMD% --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python tidak ditemukan. Pastikan Python sudah terinstall dan ada di PATH.
    pause
    exit /b 1
)

:: Check if script exists
if not exist "%SCRIPT_DIR%analisis_per_karyawan.py" (
    echo ERROR: File analisis_per_karyawan.py tidak ditemukan di direktori ini.
    pause
    exit /b 1
)

echo Pilihan analisis:
echo 1. Analisis bulan ini (default)
echo 2. Analisis bulan tertentu
echo 3. Analisis periode custom
echo 4. Analisis dengan data terbatas (untuk testing)
echo.

set /p choice="Pilih opsi (1-4, tekan Enter untuk default): "

if "%choice%"=="" set choice=1
if "%choice%"=="1" goto :run_current_month
if "%choice%"=="2" goto :run_specific_month
if "%choice%"=="3" goto :run_custom_period
if "%choice%"=="4" goto :run_limited
goto :invalid_choice

:run_current_month
echo.
echo Menjalankan analisis untuk bulan ini...
%PYTHON_CMD% "%SCRIPT_DIR%analisis_per_karyawan.py" --output-dir "%OUTPUT_DIR%" --db-path "%DB_PATH%"
goto :end

:run_specific_month
echo.
set /p month_input="Masukkan bulan (format: YYYY-MM, contoh: 2025-06): "
if "%month_input%"=="" (
    echo ERROR: Bulan tidak boleh kosong.
    goto :end
)
echo Menjalankan analisis untuk bulan %month_input%...
%PYTHON_CMD% "%SCRIPT_DIR%analisis_per_karyawan.py" --month "%month_input%" --output-dir "%OUTPUT_DIR%" --db-path "%DB_PATH%"
goto :end

:run_custom_period
echo.
set /p start_date="Masukkan tanggal mulai (format: YYYY-MM-DD): "
set /p end_date="Masukkan tanggal akhir (format: YYYY-MM-DD): "
if "%start_date%"=="" (
    echo ERROR: Tanggal mulai tidak boleh kosong.
    goto :end
)
if "%end_date%"=="" (
    echo ERROR: Tanggal akhir tidak boleh kosong.
    goto :end
)
echo Menjalankan analisis dari %start_date% hingga %end_date%...
%PYTHON_CMD% "%SCRIPT_DIR%analisis_per_karyawan.py" --start-date "%start_date%" --end-date "%end_date%" --output-dir "%OUTPUT_DIR%" --db-path "%DB_PATH%"
goto :end

:run_limited
echo.
set /p limit_input="Masukkan jumlah data maksimal (contoh: 1000): "
if "%limit_input%"=="" set limit_input=1000
echo Menjalankan analisis dengan batasan %limit_input% data...
%PYTHON_CMD% "%SCRIPT_DIR%analisis_per_karyawan.py" --limit %limit_input% --output-dir "%OUTPUT_DIR%" --db-path "%DB_PATH%"
goto :end

:invalid_choice
echo ERROR: Pilihan tidak valid.
goto :end

:end
if errorlevel 1 (
    echo.
    echo ANALISIS GAGAL! Periksa error di atas.
) else (
    echo.
    echo ANALISIS SELESAI! 
    echo Laporan tersimpan di: %OUTPUT_DIR%
    echo.
    echo Membuka folder output...
    start "" "%OUTPUT_DIR%"
)

echo.
pause 