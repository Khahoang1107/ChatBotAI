@echo off
echo ========================================
echo Auto Backup Database
echo ========================================
cd /d G:\Chatbot\ChatBotAI
backend\venv\Scripts\python.exe backup_database.py backup
echo.
echo Backup hoan tat!
pause
