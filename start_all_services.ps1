# =============================================================================
# 🚀 START ALL SERVICES - OCR System with PostgreSQL Integration
# =============================================================================

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=============================================================" -ForegroundColor Cyan
Write-Host "🚀 STARTING OCR SYSTEM WITH DATABASE INTEGRATION" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=============================================================" -ForegroundColor Cyan
Write-Host ""

# Kill existing processes
Write-Host "🔄 Stopping existing services..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Check PostgreSQL
Write-Host "`n📊 Checking PostgreSQL..." -ForegroundColor Cyan
try {
    $result = python -c "import psycopg2; conn = psycopg2.connect('postgresql://postgres:123@localhost:5432/ocr_database'); print('✅ Connected'); conn.close()" 2>&1
    if ($result -match "✅") {
        Write-Host "   ✅ PostgreSQL is running" -ForegroundColor Green
    } else {
        Write-Host "   ❌ PostgreSQL connection failed!" -ForegroundColor Red
        Write-Host "   Please start PostgreSQL and create 'ocr_database'" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "   ❌ PostgreSQL not accessible" -ForegroundColor Red
    exit 1
}

# Check if psycopg2 is installed
Write-Host "`n📦 Checking dependencies..." -ForegroundColor Cyan
python -c "import psycopg2" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ⚠️ Installing psycopg2-binary..." -ForegroundColor Yellow
    pip install psycopg2-binary --quiet
    Write-Host "   ✅ psycopg2-binary installed" -ForegroundColor Green
} else {
    Write-Host "   ✅ psycopg2-binary already installed" -ForegroundColor Green
}

# Start FastAPI Backend
Write-Host "`n🔧 Starting FastAPI Backend (port 8000)..." -ForegroundColor Cyan
$backendPath = "F:\DoAnCN\fastapi_backend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendPath'; python main.py" -WindowStyle Normal
Write-Host "   ⏳ Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check backend health
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 3 -ErrorAction Stop
    Write-Host "   ✅ Backend is running!" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️ Backend might still be starting..." -ForegroundColor Yellow
}

# Start Chatbot
Write-Host "`n🤖 Starting Chatbot (port 5001)..." -ForegroundColor Cyan
$chatbotPath = "F:\DoAnCN\chatbot"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$chatbotPath'; python app.py" -WindowStyle Normal
Write-Host "   ⏳ Waiting for chatbot to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check chatbot health
try {
    $response = Invoke-RestMethod -Uri "http://localhost:5001/health" -TimeoutSec 3 -ErrorAction Stop
    Write-Host "   ✅ Chatbot is running!" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️ Chatbot might still be starting..." -ForegroundColor Yellow
}

# Summary
Write-Host "`n" -NoNewline
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=============================================================" -ForegroundColor Cyan
Write-Host "✅ SERVICES STARTED SUCCESSFULLY!" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📡 Service Endpoints:" -ForegroundColor White
Write-Host "   • Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "   • Health:   http://localhost:8000/health" -ForegroundColor Cyan
Write-Host "   • Chatbot:  http://localhost:5001" -ForegroundColor Cyan
Write-Host "   • Chat:     http://localhost:5001/chat" -ForegroundColor Cyan
Write-Host ""
Write-Host "🗄️  Database:" -ForegroundColor White
Write-Host "   • PostgreSQL: localhost:5432" -ForegroundColor Cyan
Write-Host "   • Database:   ocr_database" -ForegroundColor Cyan
Write-Host ""
Write-Host "🧪 Test Commands:" -ForegroundColor White
Write-Host "   • Check DB:     python check_postgres.py" -ForegroundColor Yellow
Write-Host "   • Test Chatbot: python test_chatbot_db.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "📝 Upload file and check:" -ForegroundColor White
Write-Host "   1. Upload mau-hoa-don-mtt.jpg via frontend" -ForegroundColor Yellow
Write-Host "   2. Check backend logs for '✅ Saved to database'" -ForegroundColor Yellow
Write-Host "   3. Ask chatbot: 'xem dữ liệu'" -ForegroundColor Yellow
Write-Host "   4. Should see 3 invoices (2 sample + 1 new)" -ForegroundColor Yellow
Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=============================================================" -ForegroundColor Cyan
Write-Host ""

# Keep script running
Write-Host "Press any key to view service status..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Show status
Write-Host "`n📊 Current Status:" -ForegroundColor Cyan
Write-Host ""

# Check processes
$pythonProcs = Get-Process python -ErrorAction SilentlyContinue
if ($pythonProcs) {
    Write-Host "   Python processes running: $($pythonProcs.Count)" -ForegroundColor Green
    $pythonProcs | ForEach-Object {
        Write-Host "      PID $($_.Id)" -ForegroundColor Gray
    }
} else {
    Write-Host "   ⚠️ No Python processes found!" -ForegroundColor Red
}

Write-Host ""
Write-Host "To stop all services, close the PowerShell windows or run:" -ForegroundColor Yellow
Write-Host "   Get-Process python | Stop-Process -Force" -ForegroundColor Gray
Write-Host ""
