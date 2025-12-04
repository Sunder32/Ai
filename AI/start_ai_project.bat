@echo off
chcp 866 >nul
setlocal EnableDelayedExpansion

set "ROOT=%~dp0"
set "PROJECT_DIR=%ROOT%..\project"
set "FRONTEND_DIR=%ROOT%..\frontend"
set "VENV_DIR=%PROJECT_DIR%\venv"
set "MODEL_NAME=deepseek-project-model"

echo ==========================================
echo      AI PC Configurator Launcher
echo ==========================================
echo.
echo [?] ��� �������� �஥��?
echo.
echo     1 - ��� AI (⮫쪮 ᠩ�)
echo     2 - � AI ������� (%MODEL_NAME%)
echo.
set /p AI_CHOICE="�롥�� ०�� (1 ��� 2): "

if "%AI_CHOICE%"=="2" (
    set "USE_AI=true"
    echo [INFO] �����: � AI �������
) else (
    set "USE_AI=false"
    echo [INFO] �����: ��� AI
)
echo.

echo [INFO] ���� Python 3.13...
set "PYTHON_CMD="
py -3.13 --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=py -3.13"
    echo [OK] Python 3.13 ������.
) else (
    set "PYTHON_CMD=python"
)

echo [INFO] Python: !PYTHON_CMD!

if exist "%VENV_DIR%" (
    echo [OK] ����㠫쭮� ���㦥��� �������.
) else (
    echo [SETUP] �������� ����㠫쭮�� ���㦥���...
    cd /d "%PROJECT_DIR%"
    !PYTHON_CMD! -m venv venv
)

echo.
echo [INFO] ����ன�� Backend...
cd /d "%PROJECT_DIR%"
call venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py populate_db

echo.
echo [INFO] �஢�ઠ Frontend...
if not exist "%FRONTEND_DIR%\node_modules" (
    cd /d "%FRONTEND_DIR%"
    call npm install
) else (
    echo [OK] node_modules ������.
)

echo.
if "%USE_AI%"=="true" (
    echo [INFO] �஢�ઠ Ollama...
    tasklist /FI "IMAGENAME eq ollama*" 2>NUL | find /I "ollama" >NUL
    if errorlevel 1 (
        start "" ollama serve
        timeout /t 5 /nobreak >nul
    )
    echo [OK] Ollama ����饭�.
    
    echo [INFO] �஢�ઠ ������ %MODEL_NAME%...
    ollama list 2>nul | find /I "%MODEL_NAME%" >nul
    if errorlevel 1 (
        if exist "%ROOT%Modelfile" (
            cd /d "%ROOT%"
            ollama create %MODEL_NAME% -f Modelfile
        )
    )
    echo [OK] ������ ��⮢�.
    
    start "AI" cmd /k "ollama run %MODEL_NAME%"
    timeout /t 3 /nobreak >nul
) else (
    echo [INFO] AI �ய�饭.
)

echo.
echo [LAUNCH] ����� �ࢨᮢ...
start "Backend" cmd /k "cd /d "%PROJECT_DIR%" && call venv\Scripts\activate && python manage.py runserver 8001"
start "Frontend" cmd /k "cd /d "%FRONTEND_DIR%" && npm start"

echo.
echo ==========================================
echo [SUCCESS] ��⮢�!
echo ==========================================
echo   Backend:  http://localhost:8001
echo   Frontend: http://localhost:3000
if "%USE_AI%"=="true" echo   AI: %MODEL_NAME%
echo ==========================================
echo.
echo ����� ������� �� ����.
pause