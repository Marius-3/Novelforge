@echo off
setlocal EnableExtensions

cd /d "%~dp0"
set "ROOT=%CD%"

echo.
echo ========================================
echo NovelForge launcher
echo ========================================
echo.

if not exist "%ROOT%\apps\api\.venv\Scripts\python.exe" (
  echo [ERROR] Backend virtual environment was not found.
  echo Please run setup-novelforge.bat first.
  pause
  exit /b 1
)

if not exist "%ROOT%\apps\web\dist\index.html" (
  echo [ERROR] Frontend build was not found.
  echo Please run setup-novelforge.bat first.
  pause
  exit /b 1
)

cd /d "%ROOT%\apps\api"

echo Starting NovelForge backend...
echo Browser will open at http://127.0.0.1:8000
echo Press Ctrl+C in this window to stop NovelForge.
echo.

start "" "http://127.0.0.1:8000"

call ".venv\Scripts\activate.bat"
uvicorn app.main:app --host 127.0.0.1 --port 8000

pause
exit /b 0
