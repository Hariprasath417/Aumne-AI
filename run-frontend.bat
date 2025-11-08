@echo off
REM ============================================
REM Run Frontend Only
REM ============================================

echo.
echo === Starting React Frontend ===
echo.

REM Check if admin-dashboard exists
if not exist admin-dashboard (
    echo [ERROR] admin-dashboard directory not found
    pause
    exit /b 1
)

REM Navigate to frontend directory
cd admin-dashboard

echo Frontend starting on: http://localhost:3000
echo.
echo Press Ctrl+C to stop the frontend
echo.

REM Start frontend
npm start