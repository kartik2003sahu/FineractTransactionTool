@echo off
echo Clearing Fineract credentials from .env...
echo.

python -c "import os; lines = open('.env', 'r').readlines() if os.path.exists('.env') else []; open('.env', 'w').writelines([line if not line.strip().startswith('FINERACT_') else line.split('=')[0] + '=\n' for line in lines])"

echo Credentials cleared!
echo.
echo Now refresh your browser to see the login page.
echo.
pause
