# Test OCR endpoint with detailed logging
Write-Host "=== Testing OCR Upload Endpoint ===" -ForegroundColor Cyan
Write-Host ""

# Use the uploaded image
$testImage = "f:\DoAnCN\uploads\mau-hoa-don-mtt.jpg"

if (-not (Test-Path $testImage)) {
    Write-Host "❌ Test image not found!" -ForegroundColor Red
    Write-Host "Looking for: $testImage" -ForegroundColor Yellow
    
    # Try to find ANY jpg in uploads
    $anyImage = Get-ChildItem "f:\DoAnCN\uploads\*.jpg" -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($anyImage) {
        $testImage = $anyImage.FullName
        Write-Host "✅ Found alternative image: $testImage" -ForegroundColor Green
    }
    else {
        Write-Host "No images found in uploads folder" -ForegroundColor Red
        exit 1
    }
}

Write-Host "📤 Uploading: $testImage" -ForegroundColor Green
Write-Host ""

# Upload and capture full response
try {
    $response = curl.exe -X POST `
        -F "file=@$testImage" `
        http://localhost:8000/api/ocr/camera-ocr
    
    Write-Host "=== BACKEND RESPONSE ===" -ForegroundColor Yellow
    $response | ConvertFrom-Json | ConvertTo-Json -Depth 10
    Write-Host ""
    
}
catch {
    Write-Host "❌ Upload failed: $_" -ForegroundColor Red
    exit 1
}

# Check RAG stats
Write-Host "=== RAG STATISTICS ===" -ForegroundColor Cyan
$ragStats = curl.exe http://localhost:8000/chat/stats | ConvertFrom-Json
Write-Host "Total documents: $($ragStats.total_documents)" -ForegroundColor $(if ($ragStats.total_documents -gt 0) { "Green" } else { "Red" })
Write-Host "Total chunks: $($ragStats.rag_stats.total_chunks)" -ForegroundColor $(if ($ragStats.rag_stats.total_chunks -gt 0) { "Green" } else { "Red" })
