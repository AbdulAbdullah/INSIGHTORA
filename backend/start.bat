@echo off
REM Smart BI Platform - Start Server (Windows Batch)
REM Simple script to start the FastAPI development server

echo 🚀 Starting Smart BI Platform API...

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found!
    echo 💡 Run: simple_setup.sh first
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if FastAPI is installed
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo ❌ FastAPI not installed!
    echo 💡 Run: pip install -r requirements_essential.txt
    pause
    exit /b 1
)

REM Create uploads directory if it doesn't exist
if not exist "uploads" mkdir uploads

echo 🎯 Starting FastAPI server...
echo 📚 Visit http://localhost:8000/docs for API documentation
echo 🔍 Visit http://localhost:8000/health for health check
echo.
echo 🛑 Press Ctrl+C to stop
echo ========================================

REM Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000