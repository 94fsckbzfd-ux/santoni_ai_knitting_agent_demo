@echo off
setlocal

cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found in PATH.
  echo Please install Python or add it to PATH, then run this launcher again.
  pause
  exit /b 1
)

echo Starting Athena PMO Server...
echo Project root: %cd%
echo URL: http://127.0.0.1:8787/Athena.html
echo.
echo A server window will stay open. Close that window or press Ctrl+C there to stop Athena PMO Server.

start "Athena PMO Server" cmd /k python "tools\athena_pmo_server.py" --root "." --port 8787
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:8787/Athena.html"

endlocal
