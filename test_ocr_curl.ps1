#!/bin/bash
# 🧪 OCR API Test - CURL Version (for Windows PowerShell)
# ========================================================
# Sử dụng curl để test OCR API endpoints
#
# Chạy: powershell -ExecutionPolicy Bypass -File test_ocr_curl.ps1

$BASE_URL = "http://localhost:8000"

Write-Host "╔════════════════════════════════════════════════════════════════════╗" -ForegroundColor Blue
Write-Host "║              🧪 OCR API TEST - CURL COMMANDS                      ║" -ForegroundColor Blue
Write-Host "╚════════════════════════════════════════════════════════════════════╝" -ForegroundColor Blue

# TEST 1: Health Check
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "TEST 1: Health Check" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

curl -s "$BASE_URL/health" | jq '.'

# TEST 2: Get Groq Tools List
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "TEST 2: Get Groq Tools" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

curl -s "$BASE_URL/api/groq/tools" | jq '.'

# TEST 3: Simple Groq Chat
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "TEST 3: Simple Groq Chat (Blocking)" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

$payload = @{
    message = "Hóa đơn nào có tổng tiền cao nhất?"
    user_id = "test_user"
} | ConvertTo-Json

curl -s -X POST "$BASE_URL/chat/groq/simple" `
    -H "Content-Type: application/json" `
    -d $payload | jq '.'

# TEST 4: Streaming Groq Chat
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "TEST 4: Streaming Groq Chat (Real-time chunks)" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

$payload = @{
    message = "Hóa đơn nào có tổng tiền cao nhất?"
    user_id = "test_user"
} | ConvertTo-Json

Write-Host "Streaming chunks (NDJSON format):" -ForegroundColor Green
curl -s -X POST "$BASE_URL/chat/groq/stream" `
    -H "Content-Type: application/json" `
    -d $payload | ForEach-Object {
    if ($_ -match '^\{') {
        $chunk = $_ | ConvertFrom-Json
        if ($chunk.type -eq 'content') {
            Write-Host "  ⊕ $($chunk.text)" -NoNewline
        }
        elseif ($chunk.type -eq 'done') {
            Write-Host "`n  ✅ Stream completed" -ForegroundColor Green
        }
    }
}

# TEST 5: Get Invoices List
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "TEST 5: Get Invoices List" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

$payload = @{
    limit = 5
} | ConvertTo-Json

curl -s -X POST "$BASE_URL/api/invoices/list" `
    -H "Content-Type: application/json" `
    -d $payload | jq '.invoices[] | {id, invoice_code, invoice_type, buyer_name, total_amount, confidence_score}'

# TEST 6: Get Invoice Statistics
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "TEST 6: Get Invoice Statistics" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

curl -s -X GET "$BASE_URL/api/groq/tools/get_statistics" | jq '.'

Write-Host "`n✅ All tests completed!`n" -ForegroundColor Green
