#!/usr/bin/env pwsh
# Start All Services Locally (No Docker)

Write-Host "🚀 STARTING ALL SERVICES LOCALLY" -ForegroundColor Yellow
Write-Host "================================" -ForegroundColor Yellow

# Create .env files if not exist
Write-Host "`n1. Setting up environment files..." -ForegroundColor Cyan

# Backend .env
if (!(Test-Path "backend\.env")) {
    @"
# Backend Environment Variables
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///invoice.db
OPENAI_API_KEY=your-openai-api-key-here
REDIS_URL=redis://localhost:6379
MONGO_URI=mongodb://localhost:27017/invoice_db
"@ | Out-File -FilePath "backend\.env" -Encoding UTF8
    Write-Host "✅ Created backend\.env" -ForegroundColor Green
}

# Chatbot .env
if (!(Test-Path "chatbot\.env")) {
    @"
# Chatbot Environment Variables
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=True
OPENAI_API_KEY=your-openai-api-key-here
DATABASE_URL=sqlite:///chatbot.db
BACKEND_URL=http://localhost:5000
RASA_URL=http://localhost:5005
"@ | Out-File -FilePath "chatbot\.env" -Encoding UTF8
    Write-Host "✅ Created chatbot\.env" -ForegroundColor Green
}

Write-Host "`n2. Starting services..." -ForegroundColor Cyan

# Function to start service in new window
function Start-ServiceWindow($title, $directory, $command) {
    $encodedCommand = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes("cd '$directory'; $command; Read-Host 'Press Enter to exit'"))
    Start-Process powershell -ArgumentList "-WindowStyle", "Normal", "-Title", "$title", "-EncodedCommand", "$encodedCommand"
    Write-Host "✅ Started $title" -ForegroundColor Green
    Start-Sleep -Seconds 1
}

# Start backend
Write-Host "Starting Backend (Port 5000)..." -ForegroundColor Yellow
Start-ServiceWindow "Invoice Backend - Port 5000" "$(pwd)\backend" "python -m flask run --host=0.0.0.0 --port=5000"

# Start chatbot  
Write-Host "Starting Chatbot (Port 5001)..." -ForegroundColor Yellow
Start-ServiceWindow "Invoice Chatbot - Port 5001" "$(pwd)\chatbot" "python -m flask run --host=0.0.0.0 --port=5001"

# Start frontend
Write-Host "Starting Frontend (Port 5174)..." -ForegroundColor Yellow
Start-ServiceWindow "Invoice Frontend - Port 5174" "$(pwd)\frontend" "npm run dev"

Write-Host "`n🎉 ALL SERVICES STARTED!" -ForegroundColor Green
Write-Host "========================" -ForegroundColor Green
Write-Host "🌐 Access your application:" -ForegroundColor Blue
Write-Host "Frontend:  http://localhost:5174" -ForegroundColor White
Write-Host "Backend:   http://localhost:5000" -ForegroundColor White
Write-Host "Chatbot:   http://localhost:5001" -ForegroundColor White
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Yellow
Write-Host "- Each service runs in a separate PowerShell window" -ForegroundColor White
Write-Host "- Close the windows to stop the services" -ForegroundColor White
Write-Host "- Check the console output in each window for errors" -ForegroundColor White
Write-Host "- Make sure to set your OPENAI_API_KEY in .env files" -ForegroundColor White

# Wait a bit then check if services are responding
Write-Host "`n3. Checking service health (in 10 seconds)..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

# Check backend
try {
    $backendResponse = Invoke-WebRequest -Uri "http://localhost:5000" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Backend is responding" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Backend might be starting..." -ForegroundColor Yellow
}

# Check chatbot  
try {
    $chatbotResponse = Invoke-WebRequest -Uri "http://localhost:5001" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Chatbot is responding" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Chatbot might be starting..." -ForegroundColor Yellow
}

# Check frontend
try {
    $frontendResponse = Invoke-WebRequest -Uri "http://localhost:5174" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Frontend is responding" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Frontend might be starting..." -ForegroundColor Yellow
}

Write-Host "`n🚀 Development environment is ready!" -ForegroundColor Green