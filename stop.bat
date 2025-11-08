@echo off
REM ============================================
REM Stop All Services Script
REM ============================================

echo.
echo === Stopping WhatsApp Food Ordering System ===
echo.

REM Stop Python/Uvicorn processes
echo Stopping FastAPI backend...
taskkill /F /FI "WINDOWTITLE eq FastAPI Backend*" >nul 2>&1
taskkill /F /FI "IMAGENAME eq python.exe" /FI "COMMANDLINE eq *uvicorn*" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Backend stopped
) else (
    echo No backend process found
)

REM Stop Node.js processes
echo Stopping React frontend...
taskkill /F /FI "WINDOWTITLE eq React Frontend*" >nul 2>&1
taskkill /F /FI "IMAGENAME eq node.exe" /FI "COMMANDLINE eq *react-scripts*" >nul 2>&1
taskkill /F /FI "IMAGENAME eq node.exe" /FI "COMMANDLINE eq *vite*" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Frontend stopped
) else (
    echo No frontend process found
)

REM Kill processes on specific ports (fallback)
echo.
echo Checking ports...

REM Port 8000 (Backend)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
    echo [OK] Freed port 8000
)

REM Port 3000 (Frontend)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
    echo [OK] Freed port 3000
)

echo.
echo === All services stopped ===
echo.
pause