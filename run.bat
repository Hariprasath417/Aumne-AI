@echo off
REM ============================================
REM WhatsApp Food Ordering System - Run Script
REM ============================================

echo.
echo === Starting WhatsApp Food Ordering System ===
echo.

REM Check if virtual environment exists
if not exist Environment (
    echo [ERROR] Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

REM Start Backend
echo Starting FastAPI Backend...
start "FastAPI Backend" cmd /k "cd /d %CD% && Environment\Scripts\activate && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo [OK] Backend starting on http://localhost:8000
echo      API Docs: http://localhost:8000/docs
echo.

REM Wait for backend to start
echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

REM Start Frontend
if exist admin-dashboard (
    echo Starting React Frontend...
    start "React Frontend" cmd /k "cd /d %CD%\admin-dashboard && npm start"
    echo [OK] Frontend starting on http://localhost:3000
) else (
    echo [WARNING] admin-dashboard directory not found
)
echo.

echo === Services Running ===
echo Backend API: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo OpenAPI Spec: http://localhost:8000/openapi.json
if exist admin-dashboard (
    echo Frontend Dashboard: http://localhost:3000
)
echo.
echo Services are running in separate windows.
echo Close those windows to stop the services, or run stop.bat
echo.
pause