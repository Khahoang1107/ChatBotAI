#!/usr/bin/env pwsh
# Run Services Locally (No Docker) for Testing

Write-Host "🚀 STARTING SERVICES LOCALLY (NO DOCKER)" -ForegroundColor Yellow
Write-Host "=========================================" -ForegroundColor Yellow

# Check Python
Write-Host "`n1. Checking Python environment..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found! Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check Node.js
Write-Host "`n2. Checking Node.js environment..." -ForegroundColor Cyan
try {
    $nodeVersion = node --version
    $npmVersion = npm --version
    Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green
    Write-Host "✅ NPM: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found! Please install Node.js 20+" -ForegroundColor Red
    exit 1
}

# Setup backend
Write-Host "`n3. Setting up Backend (Port 5000)..." -ForegroundColor Cyan
if (Test-Path "backend/requirements.txt") {
    Write-Host "Installing backend dependencies..." -ForegroundColor Yellow
    Set-Location backend
    pip install -r requirements.txt
    Set-Location ..
    Write-Host "✅ Backend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "❌ backend/requirements.txt not found" -ForegroundColor Red
}

# Setup chatbot
Write-Host "`n4. Setting up Chatbot (Port 5001)..." -ForegroundColor Cyan
if (Test-Path "chatbot/requirements.txt") {
    Write-Host "Installing chatbot dependencies..." -ForegroundColor Yellow
    Set-Location chatbot
    pip install -r requirements.txt
    Set-Location ..
    Write-Host "✅ Chatbot dependencies installed" -ForegroundColor Green
} else {
    Write-Host "❌ chatbot/requirements.txt not found" -ForegroundColor Red
}

# Setup frontend
Write-Host "`n5. Setting up Frontend (Port 5174)..." -ForegroundColor Cyan
if (Test-Path "frontend/package.json") {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    Set-Location ..
    Write-Host "✅ Frontend dependencies installed" -ForegroundColor Green
} else {
    Write-Host "❌ frontend/package.json not found" -ForegroundColor Red
}

Write-Host "`n🎯 READY TO START SERVICES!" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green
Write-Host "💡 Run these commands in separate terminals:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Terminal 1 - Backend:" -ForegroundColor Cyan
Write-Host "cd backend && python -m flask run --host=0.0.0.0 --port=5000" -ForegroundColor White
Write-Host ""
Write-Host "Terminal 2 - Chatbot:" -ForegroundColor Cyan  
Write-Host "cd chatbot && python -m flask run --host=0.0.0.0 --port=5001" -ForegroundColor White
Write-Host ""
Write-Host "Terminal 3 - Frontend:" -ForegroundColor Cyan
Write-Host "cd frontend && npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Access URLs:" -ForegroundColor Blue
Write-Host "Frontend:  http://localhost:5174" -ForegroundColor White
Write-Host "Backend:   http://localhost:5000" -ForegroundColor White  
Write-Host "Chatbot:   http://localhost:5001" -ForegroundColor White
Write-Host ""
Write-Host "⚡ Quick Start:" -ForegroundColor Yellow
Write-Host ".\start_local_services.ps1" -ForegroundColor Cyan