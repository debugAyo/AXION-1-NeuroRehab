@echo off
cd /d "%~dp0"
echo ===============================================================
echo   Starting AXION-1 Task B: Machine Learning & Adaptive Engine
echo ===============================================================
python run_task_b.py
if errorlevel 1 (
    echo.
    echo Trying python3...
    python3 run_task_b.py
)
pause
