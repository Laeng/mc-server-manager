@echo off
title Minecraft Server Manager
echo Starting Minecraft Server Manager...
echo ====================================

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate
    echo Installing required packages...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
)

:: Create logs directory
if not exist "logs" mkdir logs

:: Run the application
echo Starting Minecraft Server Manager...
python manager/main.py

:: Keep window open on error
pause