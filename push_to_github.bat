@echo off
echo ========================================
echo Upload ChatBotAI to GitHub
echo ========================================
echo.

cd /d G:\Chatbot\ChatBotAI

echo [1/5] Checking Git installation...
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git not installed!
    echo Download: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [2/5] Adding files...
git add .

echo [3/5] Committing changes...
git commit -m "Initial commit: ChatBotAI with SQLite database and Docker support"

echo [4/5] Setting up remote (if needed)...
echo.
echo Enter your GitHub repository URL:
echo Example: https://github.com/username/ChatBotAI.git
set /p REPO_URL="Repository URL: "

if not "%REPO_URL%"=="" (
    git remote add origin %REPO_URL% 2>nul
    if errorlevel 1 (
        echo Remote origin already exists, updating...
        git remote set-url origin %REPO_URL%
    )
)

echo [5/5] Pushing to GitHub...
git push -u origin main

if errorlevel 1 (
    echo.
    echo Failed to push. Trying 'master' branch...
    git push -u origin master
)

echo.
echo ========================================
echo Upload complete!
echo ========================================
echo.
echo Your project is now on GitHub!
echo Database and backups are included.
echo.
pause
