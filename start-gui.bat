@echo off
chcp 65001 > nul
echo 正在启动 SuperPower Code Review...
python src/gui_launcher.py
if %errorlevel% neq 0 (
    echo.
    echo 启动失败，请检查 Python 是否正确安装
    pause
    exit /b 1
)