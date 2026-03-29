@echo off
chcp 65001 > nul
echo Starting SuperPower Code Review...
python src/gui_launcher.py
if %errorlevel% neq 0 (
    echo.
    echo Startup failed - please check if Python is installed correctly
    pause
    exit /b 1
)