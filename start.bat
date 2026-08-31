@echo off
echo ====================================================
echo Starting WebTest AI Platform
echo Frontend: React (Port 3000)
echo Backend: Python FastAPI (Port 4000)
echo Sandbox Target: NovaStore (Port 3001)
echo ====================================================

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH! Please install Python 3.9+.
    pause
    exit /b 1
)

pip install -r requirements.txt
npm run dev
pause
