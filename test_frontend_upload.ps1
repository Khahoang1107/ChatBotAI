# Test script to verify frontend upload flow
# This simulates what the frontend will do when uploading an image

Write-Host "=== Testing Frontend Upload Flow ===" -ForegroundColor Cyan
Write-Host ""

# Create a test image file
$testImagePath = "f:\DoAnCN\uploads\test_invoice.jpg"

if (-not (Test-Path $testImagePath)) {
    Write-Host "Error: Test image not found at $testImagePath" -ForegroundColor Red
    Write-Host "Please create a test image first" -ForegroundColor Yellow
    exit 1
}

Write-Host "1. Uploading image to backend OCR endpoint..." -ForegroundColor Green

# Upload file to backend (mimics frontend processFiles function)
$response = curl.exe -X POST `
    -F "file=@$testImagePath" `
    http://localhost:8000/api/ocr/camera-ocr

Write-Host "Backend Response:" -ForegroundColor Yellow
$response | ConvertFrom-Json | ConvertTo-Json -Depth 10

Write-Host ""
Write-Host "2. Checking RAG statistics..." -ForegroundColor Green

# Check RAG stats
$ragStats = curl.exe http://localhost:8000/chat/stats | ConvertFrom-Json
Write-Host "Total documents in RAG: $($ragStats.total_documents)" -ForegroundColor Cyan
Write-Host "Recent documents: $($ragStats.recent_documents.Count)" -ForegroundColor Cyan

Write-Host ""
Write-Host "3. Testing RAG search..." -ForegroundColor Green

# Test RAG search
$searchBody = @{
    query = "xem dữ liệu hóa đơn"
    top_k = 5
} | ConvertTo-Json

$searchResponse = curl.exe -X POST `
    -H "Content-Type: application/json" `
    -d $searchBody `
    http://localhost:8000/chat/rag-search

Write-Host "RAG Search Results:" -ForegroundColor Yellow
$searchResponse | ConvertFrom-Json | ConvertTo-Json -Depth 10

Write-Host ""
Write-Host "=== Test Complete ===" -ForegroundColor Cyan
