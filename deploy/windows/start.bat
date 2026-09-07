@echo off
rem LIMS Windows start - runs uvicorn in a minimized background window,
rem logs to backend\lims.log. Stop with deploy\windows\stop.bat.
rem Pure ASCII on purpose: cmd reads bat as ANSI/GBK on zh-CN Windows,
rem CJK chars get garbled and can corrupt parsing.
rem NOTE: no ( ) inside if-block echo lines - they would break block parsing.
cd /d "%~dp0..\..\backend"
set "PORT=8000"
set "STATIC_DIR=%~dp0..\..\frontend\dist"
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] backend\.venv not found. Run deploy\windows\setup.ps1 first.
    pause
    exit /b 1
)
start "LIMS-server" /MIN cmd /c ".venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port %PORT% 1>> lims.log 2>&1"
timeout /t 2 /nobreak >nul
netstat -ano | findstr "LISTENING" | findstr ":%PORT% " >nul
if %errorlevel% equ 0 (
    echo.
    echo LIMS is running at http://localhost:%PORT%
    echo   login: admin / lims-admin-1
    echo   logs:  backend\lims.log
    echo   stop:  deploy\windows\stop.bat
) else (
    echo.
    echo LIMS may not have started yet - check backend\lims.log
)
pause
