@echo off
set "PROJECT_MODEL_NAME=deepseek-project-model"
set "MODEL_EXISTS="
ollama list | findstr /C:"%PROJECT_MODEL_NAME%" >nul 2>&1 && set "MODEL_EXISTS=1"
if not defined MODEL_EXISTS (
  echo missing
)
