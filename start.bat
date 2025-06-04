@echo off
echo Starting Crypto Order Block Detector...
echo ========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

REM Install requirements if needed
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing/updating requirements...
pip install -r requirements.txt

echo Starting the application...
echo Open your browser and go to: http://localhost:5000
echo Press Ctrl+C to stop the server
echo ========================================

python app.py

pause 