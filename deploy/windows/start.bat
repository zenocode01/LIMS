@echo off
rem LIMS Windows daily start - double-click to run (run setup.ps1 first)
rem Pure ASCII on purpose: cmd reads bat as ANSI/GBK on zh-CN Windows,
rem CJK chars get garbled and can corrupt parsing.
cd /d "%~dp0..\..\backend"
set "STATIC_DIR=%~dp0..\..\frontend\dist"
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] venv not found at:
    echo     %cd%\.venv\Scripts\python.exe
    echo.
    echo Run the one-time setup first:
    echo     powershell -ExecutionPolicy Bypass -File deploy\windows\setup.ps1
    pause
    exit /b 1
)
.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
pause
