@echo off
echo Installing Dependencies for Multi-Estate FFB GUI
echo ===============================================
echo.

echo Installing required Python packages...
echo.

pip install pandas
if %errorlevel% neq 0 (
    echo Error installing pandas
    pause
    exit /b 1
)

pip install tkcalendar
if %errorlevel% neq 0 (
    echo Error installing tkcalendar
    pause
    exit /b 1
)

pip install fdb
if %errorlevel% neq 0 (
    echo Error installing fdb (firebird)
    pause
    exit /b 1
)

pip install reportlab
if %errorlevel% neq 0 (
    echo Error installing reportlab
    pause
    exit /b 1
)

echo.
echo All dependencies installed successfully!
echo.
echo You can now run:
echo   run_multi_estate_gui.bat
echo.
pause 