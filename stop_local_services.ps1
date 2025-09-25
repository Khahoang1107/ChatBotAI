#!/usr/bin/env pwsh
# Stop All Local Services (PowerShell version)

Write-Host "🛑 STOPPING LOCAL SERVICES" -ForegroundColor Red
Write-Host "==========================" -ForegroundColor Red

# Kill processes by name
Write-Host "`nStopping Flask processes..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -eq "python" -and $_.CommandLine -like "*flask run*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Write-Host "✅ Flask processes stopped" -ForegroundColor Green

Write-Host "`nStopping Node processes..." -ForegroundColor Yellow  
Get-Process | Where-Object {$_.ProcessName -eq "node" -and $_.CommandLine -like "*npm run dev*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Write-Host "✅ Node processes stopped" -ForegroundColor Green

# Kill processes using the ports
Write-Host "`nFreeing ports..." -ForegroundColor Yellow

try {
    netstat -ano | findstr ":5000 " | ForEach-Object { 
        $pid = ($_ -split '\s+')[-1]
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
    Write-Host "✅ Port 5000 freed" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Port 5000 was not in use" -ForegroundColor Yellow
}

try {
    netstat -ano | findstr ":5001 " | ForEach-Object {
        $pid = ($_ -split '\s+')[-1] 
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
    Write-Host "✅ Port 5001 freed" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Port 5001 was not in use" -ForegroundColor Yellow
}

try {
    netstat -ano | findstr ":5174 " | ForEach-Object {
        $pid = ($_ -split '\s+')[-1]
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue  
    }
    Write-Host "✅ Port 5174 freed" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Port 5174 was not in use" -ForegroundColor Yellow
}

Write-Host "`n🎉 All services stopped!" -ForegroundColor Green