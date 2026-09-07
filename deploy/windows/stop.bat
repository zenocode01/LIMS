@echo off
rem LIMS Windows stop - kills the process listening on the LIMS port.
rem Port-based, so it does not touch other python/node programs.
rem Pure ASCII on purpose: cmd reads bat as ANSI/GBK on zh-CN Windows.
rem NOTE: no ( ) inside if-block echo lines - they would break block parsing.
set "PORT=8000"
set "KILLED="
for /f "tokens=5" %%a in ('netstat -ano ^| findstr "LISTENING" ^| findstr ":%PORT% "') do (
    taskkill /F /PID %%a >nul 2>&1 && set "KILLED=1"
)
if defined KILLED (
    echo LIMS stopped - port %PORT% freed.
) else (
    echo LIMS is not running - nothing listening on port %PORT%.
)
pause
