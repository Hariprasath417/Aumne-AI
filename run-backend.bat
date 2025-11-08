@echo off
REM ============================================
REM Run Backend Only
REM ============================================

echo.
echo === Starting FastAPI Backend ===
echo.

REM Check if virtual environment exists
if not exist Environment (
    echo [ERROR] Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call Environment\Scripts\activate.bat

echo Backend starting on: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo OpenAPI Spec: http://localhost:8000/openapi.json
echo.
echo Press Ctrl+C to stop the backend
echo.

REM Start backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000