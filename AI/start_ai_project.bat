@echo off
setlocal EnableDelayedExpansion

:: Set paths
set "ROOT=%~dp0"
set "PROJECT_DIR=%ROOT%..\project"
set "FRONTEND_DIR=%ROOT%..\frontend"
set "VENV_DIR=%PROJECT_DIR%\venv"

echo ==========================================
echo      AI PC Configurator Launcher
echo      Target: Python 3.13
echo ==========================================
echo.

:: 1. Find Python 3.13
echo [INFO] Locating Python 3.13...
set "PYTHON_CMD="

:: Try 'py -3.13' (Windows Launcher)
py -3.13 --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=py -3.13"
    echo [INFO] Found Python 3.13 via Windows Launcher.
) else (
    :: Try direct 'python' if it happens to be 3.13
    for /f "tokens=2" %%I in ('python --version 2^>^&1') do (
        echo %%I | findstr "3.13" >nul
        if not errorlevel 1 (
            set "PYTHON_CMD=python"
            echo [INFO] System 'python' is version 3.13.
        )
    )
)

:: If still not found, check common paths or fail
if not defined PYTHON_CMD (
    if exist "C:\Python313\python.exe" (
        set "PYTHON_CMD=C:\Python313\python.exe"
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
        set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    )
)

if not defined PYTHON_CMD (
    echo [ERROR] Python 3.13 not found!
    echo [TIP] Please install Python 3.13 from python.org or the Microsoft Store.
    echo [TIP] If installed, ensure 'py' launcher is available or add it to PATH.
    echo [DEBUG] Found system python:
    python --version
    pause
    exit /b 1
)

echo [INFO] Using Python command: !PYTHON_CMD!

:: 2. Clean Environment (Force Rebuild if python version changed)
if exist "%VENV_DIR%" (
    echo.
    echo [INFO] Found existing virtual environment.
    echo [INFO] Removing old venv to ensure compatibility...
    rmdir /s /q "%VENV_DIR%"
    if exist "%VENV_DIR%" (
        echo [ERROR] Failed to remove old venv. Please delete "%VENV_DIR%" manually.
        pause
        exit /b 1
    )
    echo [SUCCESS] Old venv removed.
)

:: 3. Backend Setup
echo.
echo [INFO] Setting up Backend...

:: Create venv
echo [SETUP] Creating new virtual environment...
cd /d "%PROJECT_DIR%"
!PYTHON_CMD! -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)

:: Install dependencies
echo [SETUP] Upgrading build tools...
call venv\Scripts\activate
python -m pip install --upgrade pip setuptools wheel

echo [SETUP] Installing requirements...
:: Install core requirements
pip install -r requirements.txt

if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    echo [INFO] Trying manual install of core packages...
    pip install django djangorestframework django-cors-headers django-filter python-decouple drf-spectacular requests pillow django-ratelimit
)

:: Database setup
echo [SETUP] Applying migrations...
python manage.py migrate

echo [SETUP] Populating database...
python manage.py populate_db

:: 4. Frontend Setup
echo.
echo [INFO] Checking Frontend configuration...

:: Create .env from .env.example if it doesn't exist
if not exist "%FRONTEND_DIR%\.env" (
    echo [SETUP] Creating .env file from .env.example...
    copy "%FRONTEND_DIR%\.env.example" "%FRONTEND_DIR%\.env"
)

if not exist "%FRONTEND_DIR%\node_modules" (
    echo [SETUP] Installing frontend dependencies...
    cd /d "%FRONTEND_DIR%"
    call npm install
) else (
    echo [INFO] Frontend dependencies found. Skipping setup.
)

:: 5. Check and Start Ollama
echo.
echo [INFO] Checking Ollama AI Service...

:: Set UTF-8 encoding for proper character display
chcp 65001 >nul

:: Check if Ollama is running
tasklist /FI "IMAGENAME eq ollama*" 2>NUL | find /I "ollama" >NUL
if errorlevel 1 (
    echo [WARN] Ollama is not running. Attempting to start...
    
    :: Try to start Ollama
    where ollama >nul 2>nul
    if not errorlevel 1 (
        echo [LAUNCH] Starting Ollama service...
        start "" ollama serve
        timeout /t 5 /nobreak >nul
        echo [SUCCESS] Ollama started.
    ) else (
        echo [WARN] Ollama not found in PATH. AI features will be disabled.
        echo [TIP] Install Ollama from https://ollama.com to enable AI recommendations.
    )
) else (
    echo [SUCCESS] Ollama is already running.
)

:: 6. Start Services
echo.
echo [INFO] Starting Services...

:: Start Django with UTF-8 encoding
echo [LAUNCH] Starting Django Backend (Port 8001)...
start "AI Backend (Django)" cmd /k "chcp 65001 >nul && cd /d "%PROJECT_DIR%" && call venv\Scripts\activate && python manage.py runserver 8001"

:: Start React
echo [LAUNCH] Starting React Frontend (Port 3000)...
start "AI Frontend (React)" cmd /k "cd /d "%FRONTEND_DIR%" && npm start"

echo.
echo [SUCCESS] All services started!
echo - Backend: http://localhost:8001
echo - Frontend: http://localhost:3000
echo.
echo You can close this launcher window now.
pause
