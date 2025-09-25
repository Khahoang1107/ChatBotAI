#!/usr/bin/env pwsh
# Main Local Development Script

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("setup", "start", "stop", "test", "help")]
    [string]$Action = "help"
)

function Show-Help {
    Write-Host "🚀 LOCAL DEVELOPMENT MAIN SCRIPT" -ForegroundColor Blue
    Write-Host "=================================" -ForegroundColor Blue
    Write-Host ""
    Write-Host "Available actions:" -ForegroundColor Yellow
    Write-Host "setup  - Install all dependencies" -ForegroundColor White
    Write-Host "start  - Start all services (backend, chatbot, frontend)" -ForegroundColor White
    Write-Host "stop   - Stop all running services" -ForegroundColor White
    Write-Host "test   - Test if services are responding" -ForegroundColor White
    Write-Host "help   - Show this help message" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host ".\main.ps1 setup   # First time setup" -ForegroundColor Cyan
    Write-Host ".\main.ps1 start   # Start all services" -ForegroundColor Cyan
    Write-Host ".\main.ps1 test    # Check service health" -ForegroundColor Cyan
    Write-Host ".\main.ps1 stop    # Stop all services" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🌐 Service URLs (when running):" -ForegroundColor Blue
    Write-Host "Frontend:  http://localhost:5174" -ForegroundColor White
    Write-Host "Backend:   http://localhost:5000" -ForegroundColor White
    Write-Host "Chatbot:   http://localhost:5001" -ForegroundColor White
}

switch ($Action) {
    "setup" {
        Write-Host "🔧 Setting up local development environment..." -ForegroundColor Blue
        .\setup_local_development.ps1
    }
    "start" {
        Write-Host "🚀 Starting all services..." -ForegroundColor Green
        .\start_local_services.ps1
    }
    "stop" {
        Write-Host "🛑 Stopping all services..." -ForegroundColor Red
        .\stop_local_services.ps1
    }
    "test" {
        Write-Host "🧪 Testing all services..." -ForegroundColor Blue
        .\test_local_services.ps1
    }
    "help" {
        Show-Help
    }
    default {
        Write-Host "❌ Unknown action: $Action" -ForegroundColor Red
        Show-Help
    }
}