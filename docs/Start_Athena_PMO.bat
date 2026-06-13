@echo off
setlocal

set "ATHENA_DOCS=%~dp0"
cd /d "%ATHENA_DOCS%"

where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found in PATH.
  echo Please install Python or add it to PATH, then run this launcher again.
  pause
  exit /b 1
)

python "tools\open_athena_pmo.py"
echo.
echo Athena PMO launcher has stopped.
pause

endlocal
