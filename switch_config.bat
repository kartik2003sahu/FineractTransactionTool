@echo off
echo ========================================
echo Switch Fineract Configuration
echo ========================================
echo.
echo Available configurations:
echo 1. Production (.env.production)
echo 2. Staging (.env.staging)
echo 3. Development (.env.development)
echo 4. Custom (.env)
echo.
set /p choice="Select configuration (1-4): "

if "%choice%"=="1" (
    copy /Y .env.production .env
    echo Switched to PRODUCTION configuration
) else if "%choice%"=="2" (
    copy /Y .env.staging .env
    echo Switched to STAGING configuration
) else if "%choice%"=="3" (
    copy /Y .env.development .env
    echo Switched to DEVELOPMENT configuration
) else if "%choice%"=="4" (
    echo Using CUSTOM configuration (.env)
) else (
    echo Invalid choice!
    pause
    exit /b 1
)

echo.
echo Configuration active. Restart the tool for changes to take effect.
echo.
pause
