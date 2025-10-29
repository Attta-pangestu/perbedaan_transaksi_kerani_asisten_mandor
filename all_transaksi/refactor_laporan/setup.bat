@echo off
echo ====================================================
echo FFB Analysis System - Setup and Installation
echo ====================================================
echo.

:: Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher and try again
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Show Python version
echo Python found:
python --version

:: Check if in correct directory
if not exist "main.py" (
    echo ERROR: main.py not found. Please run this script from the refactor_laporan directory.
    pause
    exit /b 1
)

echo.
echo Installing Python dependencies...
echo This may take a few minutes...
echo.

:: Install dependencies
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo Dependencies installed successfully!
echo.

:: Test database connections
echo Testing database connections...
echo.

python main.py --test-connections
if %errorlevel% neq 0 (
    echo WARNING: Some database connections failed
    echo Please check your database configuration
    echo.
)

:: Create desktop shortcut
echo Creating desktop shortcut...
echo.

set "shortcut_path=%USERPROFILE%\Desktop\FFB Analysis System.lnk"
set "target_path=%cd%\main.py"
set "working_dir=%cd%"

powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%shortcut_path%'); $Shortcut.TargetPath = 'python'; $Shortcut.Arguments = '\"%target_path%\"'; $Shortcut.WorkingDirectory = '%working_dir%'; $Shortcut.IconLocation = 'python.exe,0'; $Shortcut.Description = 'FFB Analysis System'; $Shortcut.Save()"

if %errorlevel% equ 0 (
    echo Desktop shortcut created successfully!
) else (
    echo WARNING: Could not create desktop shortcut
    echo You can still run the application from this folder
)

echo.
echo ====================================================
echo Setup Complete!
echo ====================================================
echo.
echo To start the application:
echo 1. Double-click the desktop shortcut (if created)
echo 2. Or run: python main.py
echo 3. Or double-click main.py
echo.
echo For help and documentation, see the docs/ folder.
echo.
pause