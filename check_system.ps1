# Comprehensive System Check and Restart
Write-Host "════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   KIỂM TRA HỆ THỐNG INVOICE AI" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check current status
Write-Host "📋 BƯỚC 1: Kiểm tra trạng thái hiện tại" -ForegroundColor Yellow
Write-Host "─────────────────────────────────────" -ForegroundColor Gray

$backendPort = netstat -ano | Select-String ":8000" | Select-String "LISTENING"
$chatbotPort = netstat -ano | Select-String ":5001" | Select-String "LISTENING"

Write-Host "Backend (Port 8000): " -NoNewline
if ($backendPort) {
    Write-Host "✅ RUNNING" -ForegroundColor Green
    $backendStatus = $true
}
else {
    Write-Host "❌ STOPPED" -ForegroundColor Red
    $backendStatus = $false
}

Write-Host "Chatbot (Port 5001): " -NoNewline
if ($chatbotPort) {
    Write-Host "✅ RUNNING" -ForegroundColor Green
    $chatbotStatus = $true
}
else {
    Write-Host "❌ STOPPED" -ForegroundColor Red
    $chatbotStatus = $false
}

Write-Host ""

# Step 2: Test connectivity
if ($backendStatus) {
    Write-Host "📊 BƯỚC 2: Kiểm tra Backend API" -ForegroundColor Yellow
    Write-Host "─────────────────────────────────────" -ForegroundColor Gray
    
    # Test health endpoint
    try {
        $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5
        Write-Host "Health Check: ✅ $($health.status)" -ForegroundColor Green
    }
    catch {
        Write-Host "Health Check: ❌ Failed - $_" -ForegroundColor Red
        $backendStatus = $false
    }
    
    # Test RAG stats
    if ($backendStatus) {
        try {
            $stats = Invoke-RestMethod -Uri "http://localhost:8000/chat/stats" -Method Get -TimeoutSec 5
            Write-Host "RAG Documents: $($stats.total_documents)" -ForegroundColor $(if ($stats.total_documents -gt 0) { "Green" } else { "Yellow" })
            Write-Host "RAG Chunks: $($stats.rag_stats.total_chunks)" -ForegroundColor $(if ($stats.rag_stats.total_chunks -gt 0) { "Green" } else { "Yellow" })
            
            if ($stats.total_documents -eq 0) {
                Write-Host "⚠️ RAG database is empty. Please upload invoices." -ForegroundColor Yellow
            }
        }
        catch {
            Write-Host "RAG Stats: ❌ Failed to get stats" -ForegroundColor Red
        }
    }
    
    Write-Host ""
}

if ($chatbotStatus) {
    Write-Host "🤖 BƯỚC 3: Kiểm tra Chatbot" -ForegroundColor Yellow
    Write-Host "─────────────────────────────────────" -ForegroundColor Gray
    
    try {
        $chatHealth = Invoke-RestMethod -Uri "http://localhost:5001/health" -Method Get -TimeoutSec 5
        Write-Host "Chatbot Health: ✅ OK" -ForegroundColor Green
    }
    catch {
        Write-Host "Chatbot Health: ❌ Failed" -ForegroundColor Red
        $chatbotStatus = $false
    }
    
    Write-Host ""
}

# Step 3: Test RAG Search if both running
if ($backendStatus -and $chatbotStatus) {
    Write-Host "🔍 BƯỚC 4: Test RAG Semantic Search" -ForegroundColor Yellow
    Write-Host "─────────────────────────────────────" -ForegroundColor Gray
    
    try {
        $searchBody = @{
            query = "hóa đơn"
            top_k = 3
        } | ConvertTo-Json
        
        $searchResult = Invoke-RestMethod -Uri "http://localhost:8000/chat/rag-search" `
            -Method Post `
            -Body $searchBody `
            -ContentType "application/json" `
            -TimeoutSec 10
        
        $resultCount = $searchResult.results.Count
        Write-Host "Search Results: $resultCount documents found" -ForegroundColor $(if ($resultCount -gt 0) { "Green" } else { "Yellow" })
        
        if ($resultCount -gt 0) {
            Write-Host ""
            Write-Host "Top 3 Results:" -ForegroundColor Cyan
            for ($i = 0; $i -lt [Math]::Min(3, $resultCount); $i++) {
                $result = $searchResult.results[$i]
                $similarity = [math]::Round((1 - $result.distance) * 100, 2)
                Write-Host "  $($i+1). Similarity: $similarity%" -ForegroundColor Green
                Write-Host "     Preview: $($result.content.Substring(0, [Math]::Min(80, $result.content.Length)))..." -ForegroundColor Gray
            }
        }
    }
    catch {
        Write-Host "RAG Search: ❌ Failed - $_" -ForegroundColor Red
    }
    
    Write-Host ""
}

# Step 4: Summary and recommendations
Write-Host "════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   KẾT QUẢ KIỂM TRA" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

if ($backendStatus -and $chatbotStatus) {
    Write-Host "✅ HỆ THỐNG HOẠT ĐỘNG BÌNH THƯỜNG" -ForegroundColor Green
    Write-Host ""
    Write-Host "Bạn có thể:" -ForegroundColor White
    Write-Host "  • Upload hóa đơn tại: http://localhost:3001" -ForegroundColor Cyan
    Write-Host "  • Query ví dụ: 'xem hóa đơn đã lưu'" -ForegroundColor Cyan
    Write-Host "  • Query ví dụ: 'hiển thị dữ liệu hóa đơn'" -ForegroundColor Cyan
}
else {
    Write-Host "❌ HỆ THỐNG CÓ VẤN ĐỀ" -ForegroundColor Red
    Write-Host ""
    Write-Host "Cần khởi động lại services:" -ForegroundColor Yellow
    Write-Host ""
    
    if (-not $backendStatus) {
        Write-Host "Khởi động Backend:" -ForegroundColor White
        Write-Host "  cd f:\DoAnCN\fastapi_backend" -ForegroundColor Gray
        Write-Host "  poetry run python main.py" -ForegroundColor Gray
        Write-Host ""
    }
    
    if (-not $chatbotStatus) {
        Write-Host "Khởi động Chatbot:" -ForegroundColor White
        Write-Host "  cd f:\DoAnCN\chatbot" -ForegroundColor Gray
        Write-Host "  python app.py" -ForegroundColor Gray
        Write-Host ""
    }
    
    Write-Host "Hoặc chạy script tự động:" -ForegroundColor Yellow
    Write-Host "  .\start_all_services.ps1" -ForegroundColor Gray
}

Write-Host ""
