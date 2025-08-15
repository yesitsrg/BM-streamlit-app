@echo off
echo ================================================
echo  Beisman Maps FastAPI Application
echo  New Mexico Highlands University
echo ================================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo Python found!
python --version

echo.
echo Checking virtual environment...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing/updating dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Creating static directories...
if not exist "static" mkdir static
if not exist "static\css" mkdir static\css
if not exist "static\js" mkdir static\js
if not exist "static\images" mkdir static\images

echo.
echo Creating placeholder images...
if not exist "static\images\university-logo.png" (
    echo Creating placeholder university logo...
    echo. > static\images\university-logo.png
)

if not exist "static\images\warning-icon.png" (
    echo Creating placeholder warning icon...
    echo. > static\images\warning-icon.png
)

echo.
echo Testing database connection...
python -c "from database import DatabaseManager; db = DatabaseManager(); print('Database test:', 'PASSED' if db.test_connection() else 'FAILED - Check your database configuration')"

echo.
echo ================================================
echo  Starting Beisman Maps Application
echo ================================================
echo.
echo Application will be available at:
echo   Main App: http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo   Health:   http://localhost:8000/api/health
echo.
echo Default Admin Credentials:
echo   Username: admin
echo   Password: admin
echo.
echo Press Ctrl+C to stop the server
echo ================================================
echo.

python main.py

echo.
echo Application stopped.
pause
