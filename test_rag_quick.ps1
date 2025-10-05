# Quick RAG Test Script
Write-Host "=== Testing RAG Database ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: Check RAG stats
Write-Host "1️⃣ Checking RAG statistics..." -ForegroundColor Yellow
$stats = curl.exe http://localhost:8000/chat/stats | ConvertFrom-Json
Write-Host "Total documents: $($stats.total_documents)" -ForegroundColor $(if ($stats.total_documents -gt 0) { "Green" } else { "Red" })
Write-Host "Total chunks: $($stats.rag_stats.total_chunks)" -ForegroundColor $(if ($stats.rag_stats.total_chunks -gt 0) { "Green" } else { "Red" })
Write-Host ""

# Test 2: RAG Search
Write-Host "2️⃣ Testing RAG search..." -ForegroundColor Yellow
$searchQuery = @{
    query = "hóa đơn"
    top_k = 5
} | ConvertTo-Json

$searchResult = curl.exe -X POST `
    -H "Content-Type: application/json" `
    -d $searchQuery `
    http://localhost:8000/chat/rag-search | ConvertFrom-Json

Write-Host "Found $($searchResult.results.Count) documents" -ForegroundColor $(if ($searchResult.results.Count -gt 0) { "Green" } else { "Red" })

if ($searchResult.results.Count -gt 0) {
    Write-Host ""
    Write-Host "📄 Sample results:" -ForegroundColor Cyan
    $searchResult.results | Select-Object -First 3 | ForEach-Object {
        Write-Host "  - Doc ID: $($_.document_id)"
        Write-Host "    Content: $($_.content.Substring(0, [Math]::Min(100, $_.content.Length)))..."
        Write-Host ""
    }
}

# Test 3: Test chatbot query
Write-Host "3️⃣ Testing chatbot data query..." -ForegroundColor Yellow
$chatQuery = @{
    message = "xem các hóa đơn đã lưu"
    user_id = "test_user"
} | ConvertTo-Json

$chatResult = curl.exe -X POST `
    -H "Content-Type: application/json" `
    -d $chatQuery `
    http://localhost:5001/chat | ConvertFrom-Json

Write-Host "Chatbot response:" -ForegroundColor Cyan
Write-Host $chatResult.message
