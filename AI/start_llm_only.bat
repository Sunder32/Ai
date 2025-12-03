@echo off
setlocal

:: Root
set "ROOT=%~dp0"
cd /d "%ROOT%"

:: Config: which Modelfile and model name to use
set "MODEL_FILE=Modelfile"
set "PROJECT_MODEL_NAME=deepseek-project-model"
set "PORT=5050"

:: Prefer working local venv Python; fall back to system python
set "PY_CMD=%ROOT%.venv\Scripts\python.exe"
if exist "%PY_CMD%" (
    "%PY_CMD%" --version >nul 2>&1
    if errorlevel 1 (
        echo [WARN] Local .venv looks broken; using system Python.
        set "PY_CMD=python"
    )
) else (
    set "PY_CMD=python"
)
echo [INFO] Using Python: %PY_CMD%
echo [INFO] Model: %PROJECT_MODEL_NAME% ^| Modelfile: %MODEL_FILE%

:: Required tools
"%PY_CMD%" --version >nul 2>&1 || goto :no_python
ollama --version >nul 2>&1     || goto :no_ollama

:: Local Ollama models dir
set "OLLAMA_MODELS=%ROOT%ollama_data"
if not exist "%OLLAMA_MODELS%" mkdir "%OLLAMA_MODELS%"

:: Start Ollama if needed
tasklist /FI "IMAGENAME eq ollama.exe" /NH | findstr /I "ollama.exe" >nul
if errorlevel 1 (
    echo [INFO] Starting Ollama...
    start "" /B ollama serve
    timeout /t 3 /nobreak >nul
)

:: Ensure project model exists
echo [INFO] Ensuring model %PROJECT_MODEL_NAME% exists...
ollama show %PROJECT_MODEL_NAME% >nul 2>&1
if errorlevel 1 (
    if not exist "%MODEL_FILE%" goto :no_modelfile
    ollama create %PROJECT_MODEL_NAME% -f "%ROOT%%MODEL_FILE%" || goto :create_fail
)

:: Python deps (best effort)
if exist "requirements.txt" goto :pip_install
goto :after_pip

:pip_install
echo [INFO] Installing Python deps (requirements.txt)...
call "%PY_CMD%" -m pip install -r requirements.txt >nul
:after_pip

:: Start FastAPI backend with the chosen model (in this window)
echo [INFO] Starting FastAPI on http://localhost:%PORT% using model %PROJECT_MODEL_NAME% ...
start "" http://localhost:%PORT%
set PROJECT_MODEL_NAME=%PROJECT_MODEL_NAME%
set PORT=%PORT%
%PY_CMD% server\main.py

echo [WARN] FastAPI process stopped. See messages above.
pause
endlocal
exit /b 0

:no_python
echo [ERR] Python not found. Install Python 3.10+.
pause
exit /b 1

:no_ollama
echo [ERR] Ollama not found in PATH. Install or add to PATH.
pause
exit /b 1

:no_modelfile
echo [ERR] Model file %MODEL_FILE% not found. Edit start_llm_only.bat to set MODEL_FILE.
pause
exit /b 1

:create_fail
echo [ERR] Failed to create model. Check Modelfile and GPU availability.
pause
exit /b 1
