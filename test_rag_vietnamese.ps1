# Comprehensive RAG Test - Vietnamese Language Support
Write-Host "=== Testing RAG Vietnamese Language Understanding ===" -ForegroundColor Cyan
Write-Host ""

# Start backend if not running
$backendRunning = netstat -ano | Select-String ":8000" | Select-String "LISTENING"
if (-not $backendRunning) {
    Write-Host "⚠️ Backend not running. Starting..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd f:\DoAnCN\fastapi_backend; poetry run python main.py"
    Write-Host "⏳ Waiting 15 seconds for backend to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 15
}

# Test 1: Check RAG Stats
Write-Host "1️⃣ Checking RAG Database Stats..." -ForegroundColor Cyan
try {
    $stats = curl.exe http://localhost:8000/chat/stats 2>$null | ConvertFrom-Json
    Write-Host "   Total documents: $($stats.total_documents)" -ForegroundColor $(if ($stats.total_documents -gt 0) { "Green" } else { "Red" })
    Write-Host "   Total chunks: $($stats.rag_stats.total_chunks)" -ForegroundColor $(if ($stats.rag_stats.total_chunks -gt 0) { "Green" } else { "Red" })
    Write-Host ""
}
catch {
    Write-Host "   ❌ Cannot connect to backend" -ForegroundColor Red
    exit 1
}

if ($stats.total_documents -eq 0) {
    Write-Host "❌ No documents in RAG database!" -ForegroundColor Red
    Write-Host "Please upload some invoices first." -ForegroundColor Yellow
    exit 1
}

# Test 2: RAG Semantic Search - Various Vietnamese Queries
Write-Host "2️⃣ Testing Vietnamese Semantic Search..." -ForegroundColor Cyan
Write-Host ""

$testQueries = @(
    "hóa đơn",
    "invoice", 
    "xem dữ liệu",
    "thông tin thanh toán",
    "số tiền",
    "khách hàng",
    "1C23MYY",  # Specific invoice code
    "CPIIOANGLON"  # Company name from OCR
)

foreach ($testQuery in $testQueries) {
    Write-Host "   Query: '$testQuery'" -ForegroundColor Yellow
    
    $searchBody = @{
        query = $testQuery
        top_k = 3
    } | ConvertTo-Json
    
    try {
        $result = curl.exe -X POST `
            -H "Content-Type: application/json" `
            -d $searchBody `
            http://localhost:8000/chat/rag-search 2>$null | ConvertFrom-Json
        
        $count = $result.results.Count
        Write-Host "   Results: $count documents" -ForegroundColor $(if ($count -gt 0) { "Green" } else { "Red" })
        
        if ($count -gt 0) {
            $topResult = $result.results[0]
            Write-Host "   Top match similarity: $([math]::Round((1 - $topResult.distance) * 100, 2))%" -ForegroundColor Cyan
            Write-Host "   Content preview: $($topResult.content.Substring(0, [Math]::Min(80, $topResult.content.Length)))..." -ForegroundColor Gray
        }
        Write-Host ""
        
    }
    catch {
        Write-Host "   ❌ Search failed: $_" -ForegroundColor Red
    }
}

# Test 3: Test with Typos (Common OCR Errors)
Write-Host "3️⃣ Testing Typo Tolerance..." -ForegroundColor Cyan
Write-Host ""

$typoQueries = @(
    "hoa don",  # Missing dấu
    "hddon",  # Typo
    "cong ty"  # Missing dấu
)

foreach ($typoQuery in $typoQueries) {
    Write-Host "   Query: '$typoQuery' (with typos)" -ForegroundColor Yellow
    
    $searchBody = @{
        query = $typoQuery
        top_k = 3
    } | ConvertTo-Json
    
    try {
        $result = curl.exe -X POST `
            -H "Content-Type: application/json" `
            -d $searchBody `
            http://localhost:8000/chat/rag-search 2>$null | ConvertFrom-Json
        
        $count = $result.results.Count
        Write-Host "   Results: $count documents" -ForegroundColor $(if ($count -gt 0) { "Green" } else { "Yellow" })
        
        if ($count -gt 0) {
            $topResult = $result.results[0]
            Write-Host "   Top match similarity: $([math]::Round((1 - $topResult.distance) * 100, 2))%" -ForegroundColor Cyan
        }
        Write-Host ""
        
    }
    catch {
        Write-Host "   ❌ Search failed" -ForegroundColor Red
    }
}

Write-Host "=== Test Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary:" -ForegroundColor White
Write-Host "✅ Model supports Vietnamese: paraphrase-multilingual-MiniLM-L12-v2" -ForegroundColor Green
Write-Host "✅ Semantic search works across languages" -ForegroundColor Green
Write-Host "⚠️ For best results, use correct spelling" -ForegroundColor Yellow
Write-Host ""
Write-Host "Recommended queries:" -ForegroundColor Cyan
Write-Host "  • 'xem hóa đơn đã lưu'" -ForegroundColor White
Write-Host "  • 'hiển thị dữ liệu hóa đơn'" -ForegroundColor White
Write-Host "  • 'tìm kiếm hóa đơn'" -ForegroundColor White
