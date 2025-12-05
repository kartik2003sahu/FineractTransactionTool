@echo off
echo ========================================
echo Fineract Transaction Tool Setup
echo ========================================
echo.

:: Check Python
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo.

:: Install dependencies
echo [2/4] Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

:: Create .env if not exists
echo [3/4] Setting up configuration...
if not exist .env (
    echo Creating .env file from template...
    copy .env.template .env
    echo.
    echo IMPORTANT: Please edit .env file with your Fineract server details!
    echo.
) else (
    echo .env file already exists - skipping
    echo.
)

:: Create desktop folder
echo [4/4] Creating data folders...
if not exist ..\desktop mkdir ..\desktop
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file with your Fineract credentials
echo 2. Run: python main.py
echo 3. Open browser: http://localhost:8000
echo.
pause
