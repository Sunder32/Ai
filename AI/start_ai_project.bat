@echo off
chcp 65001 >nul
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
echo [?] Как запустить проект?
echo.
echo     1 - Без AI (только сайт)
echo     2 - С AI моделью (%MODEL_NAME%)
echo.
set /p AI_CHOICE="Выберите режим (1 или 2): "

if "%AI_CHOICE%"=="2" (
    set "USE_AI=true"
    echo [INFO] Режим: С AI моделью
) else (
    set "USE_AI=false"
    echo [INFO] Режим: Без AI
)
echo.

echo [INFO] Поиск Python 3.13...
set "PYTHON_CMD="
py -3.13 --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=py -3.13"
    echo [OK] Python 3.13 найден.
) else (
    set "PYTHON_CMD=python"
)

echo [INFO] Python: !PYTHON_CMD!

if exist "%VENV_DIR%" (
    echo [OK] Виртуальное окружение найдено.
) else (
    echo [SETUP] Создание виртуального окружения...
    cd /d "%PROJECT_DIR%"
    !PYTHON_CMD! -m venv venv
)

echo.
echo [INFO] Настройка Backend...
cd /d "%PROJECT_DIR%"
call venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py populate_db

echo.
echo [INFO] Проверка Frontend...
if not exist "%FRONTEND_DIR%\node_modules" (
    cd /d "%FRONTEND_DIR%"
    call npm install
) else (
    echo [OK] node_modules найден.
)

echo.
if "%USE_AI%"=="true" (
    echo [INFO] Проверка Ollama...
    tasklist /FI "IMAGENAME eq ollama*" 2>NUL | find /I "ollama" >NUL
    if errorlevel 1 (
        start "" ollama serve
        timeout /t 5 /nobreak >nul
    )
    echo [OK] Ollama запущена.
    
    echo [INFO] Проверка модели %MODEL_NAME%...
    ollama list 2>nul | find /I "%MODEL_NAME%" >nul
    if errorlevel 1 (
        if exist "%ROOT%Modelfile" (
            cd /d "%ROOT%"
            ollama create %MODEL_NAME% -f Modelfile
        )
    )
    echo [OK] Модель готова.
    
    start "AI" cmd /k "ollama run %MODEL_NAME%"
    timeout /t 3 /nobreak >nul
) else (
    echo [INFO] AI пропущен.
)

echo.
echo [LAUNCH] Запуск сервисов...
start "Backend" cmd /k "cd /d "%PROJECT_DIR%" && call venv\Scripts\activate && python manage.py runserver 8001"
start "Frontend" cmd /k "cd /d "%FRONTEND_DIR%" && npm start"

echo.
echo ==========================================
echo [SUCCESS] Готово!
echo ==========================================
echo   Backend:  http://localhost:8001
echo   Frontend: http://localhost:3000
if "%USE_AI%"=="true" echo   AI: %MODEL_NAME%
echo ==========================================
echo.
echo Нажмите любую клавишу для выхода.
pause
