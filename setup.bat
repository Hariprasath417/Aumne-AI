@echo off
REM ============================================
REM WhatsApp Food Ordering System - Setup Script
REM ============================================

echo.
echo === WhatsApp Food Ordering System Setup ===
echo.

REM Check if Python is installed
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.8+ from python.org
    pause
    exit /b 1
)
echo [OK] Python found
echo.

REM Check if Node.js is installed
echo Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found. Please install Node.js from nodejs.org
    pause
    exit /b 1
)
echo [OK] Node.js found
echo.

REM ============================================
REM Backend Setup
REM ============================================
echo === Setting up FastAPI Backend ===
echo.

REM Create virtual environment
echo Creating Python virtual environment...
if exist Environment (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv Environment
    echo [OK] Virtual environment created
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call Environment\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install backend dependencies
echo Installing backend dependencies...
if exist requirements.txt (
    pip install -r requirements.txt --quiet
    echo [OK] Backend dependencies installed
) else (
    echo Creating requirements.txt...
    (
        echo fastapi==0.104.1
        echo uvicorn[standard]==0.24.0
        echo python-dotenv==1.0.0
        echo twilio==8.10.0
        echo pydantic==2.5.0
        echo python-multipart==0.0.6
        echo httpx==0.25.2
    ) > requirements.txt
    pip install -r requirements.txt --quiet
    echo [OK] Default dependencies installed
)
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env configuration file...
    (
        echo # WhatsApp API Configuration
        echo TWILIO_ACCOUNT_SID=your_account_sid_here
        echo TWILIO_AUTH_TOKEN=your_auth_token_here
        echo TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
        echo.
        echo # FastAPI Configuration
        echo HOST=localhost
        echo PORT=8000
        echo RELOAD=True
        echo.
        echo # CORS Configuration
        echo ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
    ) > .env
    echo [OK] .env file created. Please update with your credentials!
)
echo.

REM ============================================
REM Frontend Setup
REM ============================================
echo === Setting up React Frontend ===
echo.

if exist admin-dashboard (
    cd admin-dashboard
    
    echo Installing frontend dependencies...
    call npm install
    echo [OK] Frontend dependencies installed
    echo.
    
    REM Create .env file for frontend
    if not exist .env (
        echo Creating frontend .env file...
        (
            echo VITE_API_URL=http://localhost:8000
            echo REACT_APP_API_URL=http://localhost:8000
        ) > .env
        echo [OK] Frontend .env file created
    )
    
    cd ..
) else (
    echo [ERROR] admin-dashboard directory not found
)
echo.

REM ============================================
REM Install OpenAPI Generator
REM ============================================
echo === Setting up OpenAPI Generator ===
echo.

REM Check if Java is installed
echo Checking Java installation...
java -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Java not found. Required for OpenAPI Generator.
    echo Please install Java 11+ from oracle.com
) else (
    echo [OK] Java found
)
echo.

echo Installing OpenAPI Generator CLI...
call npm install -g @openapitools/openapi-generator-cli
echo [OK] OpenAPI Generator CLI installed
echo.

REM ============================================
REM Summary
REM ============================================
echo.
echo === Setup Complete ===
echo.
echo Next Steps:
echo 1. Update .env file with your WhatsApp API credentials
echo 2. Run 'run.bat' to start both backend and frontend
echo 3. Run 'generate-sdk.bat' to generate Python SDK
echo.
echo Documentation:
echo - Backend API: http://localhost:8000/docs
echo - OpenAPI JSON: http://localhost:8000/openapi.json
echo - Frontend: http://localhost:3000
echo.
pause