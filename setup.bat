@echo off
SETLOCAL

:: Script to set up and run Mudhumeni AI on Windows

:: Print colored messages - Windows version
CALL :print_header "Mudhumeni AI Setup"

:: Check if Python 3 is installed
python --version > NUL 2>&1
IF %ERRORLEVEL% NEQ 0 (
    CALL :print_error "Python is not installed. Please install Python 3.9 or higher."
    EXIT /B 1
)

:: Check Python version
FOR /F "tokens=2" %%I IN ('python --version') DO SET PYTHON_VERSION=%%I
ECHO Python version %PYTHON_VERSION% detected.

:: Create virtual environment if it doesn't exist
IF NOT EXIST venv (
    ECHO Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
ECHO Activating virtual environment...
CALL venv\Scripts\activate.bat

:: Install dependencies
ECHO Installing dependencies...
pip install -r requirements.txt

:: Check if .env file exists
IF NOT EXIST .env (
    ECHO Creating .env file...
    (
    ECHO GROQ_API_KEY=your_groq_api_key_here
    ECHO MONGODB_URI=mongodb://localhost:27017/mudhumeni_db
    ECHO FLASK_SECRET_KEY=^%RANDOM%%RANDOM%%RANDOM%%RANDOM%
    ) > .env
    ECHO .env file created. Please edit it with your actual API keys.
)

:: Ask if user wants to train the model
SET /P TRAIN_MODEL="Do you want to train the model? (y/n): "
IF /I "%TRAIN_MODEL%"=="y" (
    ECHO Training model...
    python train_model.py
)

:: Ask if user wants to run the application
SET /P RUN_APP="Do you want to run the application? (y/n): "
IF /I "%RUN_APP%"=="y" (
    ECHO Running Mudhumeni AI...
    python app.py
) ELSE (
    ECHO Setup complete. Run 'python app.py' to start the application.
)

GOTO :EOF

:print_header
ECHO.
ECHO =======================================================
ECHO %~1
ECHO =======================================================
ECHO.
GOTO :EOF

:print_error
ECHO ERROR: %~1
GOTO :EOF

ENDLOCAL