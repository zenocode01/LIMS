@echo off
rem LIMS Windows 日常启动 — 双击即用（先跑过 setup.ps1）
cd /d "%~dp0..\..\backend"
set "STATIC_DIR=%~dp0..\..\frontend\dist"
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] backend\.venv 不存在，请先运行 deploy\windows\setup.ps1
    pause
    exit /b 1
)
.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
pause
