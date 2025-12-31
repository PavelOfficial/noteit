@echo off
echo Starting NoteIt Application...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not found in PATH.
    echo Please install Python 3.8+ and add it to PATH.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create .env if it doesn't exist
if not exist ".env" (
    echo Creating .env file...
    if exist ".env.example" (
        copy .env.example .env >nul 2>&1
        echo Warning: .env created from .env.example. Please ensure SECRET_KEY is set to a random value!
        echo Generate a new SECRET_KEY with: python -c "import secrets; print(secrets.token_hex(32))"
    ) else (
        echo FLASK_APP=app.py > .env
        echo FLASK_ENV=development >> .env
        echo Generating SECRET_KEY...
        python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))" >> .env
        echo DATABASE_URL=sqlite:///noteit.db >> .env
        echo.
        echo .env file created with a random SECRET_KEY
    )
)

REM Run the application
echo.
echo Starting NoteIt on http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python app.py

pause

