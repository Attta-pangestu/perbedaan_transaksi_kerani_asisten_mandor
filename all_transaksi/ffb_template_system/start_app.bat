@echo off
echo Starting FFB Template System...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if we're in the correct directory
if not exist "src\app.py" (
    echo Error: src\app.py not found
    echo Please make sure you're running this script from the ffb_template_system directory
    pause
    exit /b 1
)

REM Check if requirements.txt exists
if not exist "requirements.txt" (
    echo Warning: requirements.txt not found
    echo You may need to install dependencies manually
    echo.
)

REM Create necessary directories if they don't exist
echo Creating necessary directories...
if not exist "logs" mkdir logs
if not exist "templates" mkdir templates
if not exist "templates\jasper" mkdir templates\jasper
if not exist "templates\uploads" mkdir templates\uploads
if not exist "reports" mkdir reports
if not exist "temp" mkdir temp
if not exist "temp\jasper" mkdir temp\jasper

REM Check if config.json exists
if not exist "config.json" (
    echo Warning: config.json not found
    echo Creating default configuration file...
    (
        echo {
        echo   "estates": [
        echo     {
        echo       "name": "PGE 1A",
        echo       "path": "C:/Database/PGE1A.FDB",
        echo       "host": "localhost",
        echo       "port": 3050
        echo     }
        echo   ],
        echo   "jasper": {
        echo     "compiler_path": "C:/Program Files/JasperSoft/jasperreports/lib",
        echo     "temp_dir": "temp/jasper"
        echo   },
        echo   "logging": {
        echo     "level": "INFO",
        echo     "file": "logs/app.log"
        echo   },
        echo   "flask": {
        echo     "secret_key": "your-secret-key-change-this-in-production",
        echo     "debug": true,
        echo     "host": "0.0.0.0",
        echo     "port": 5000
        echo   }
        echo }
    ) > config.json
    echo Default config.json created. Please update with your actual database paths.
    echo.
)

REM Check if Node.js is installed for frontend dependencies
node --version >nul 2>&1
if errorlevel 1 (
    echo Warning: Node.js not found. Frontend build tools may not work.
    echo Please install Node.js for full frontend functionality.
    echo.
)

REM Install Python dependencies if needed
echo Checking Python dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo Installing Python dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        echo Please check your internet connection and Python setup
        pause
        exit /b 1
    )
    echo Dependencies installed successfully.
    echo.
)

REM Set environment variables
set FLASK_APP=src.app
set FLASK_ENV=development
set PYTHONPATH=%CD%

echo.
echo ========================================
echo FFB Template System
echo ========================================
echo.
echo Starting application...
echo.
echo Application will be available at:
echo http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

REM Start the Flask application
python src/app.py

REM If the application exits, show a message
echo.
echo Application stopped.
pause