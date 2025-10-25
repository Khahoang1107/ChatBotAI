@echo off
REM 🧪 OCR API Test Commands - Copy/Paste từng command vào PowerShell
REM ================================================================

REM ============ TEST 1: Health Check ============
REM Kiểm tra server có running không
curl -s http://localhost:8000/health | jq .

REM ============ TEST 2: Get Groq Tools ============
REM Lấy danh sách 7 tools
curl -s http://localhost:8000/api/groq/tools | jq .

REM ============ TEST 3: Simple Chat ============
REM Chat blocking (chặn cho đến hết)
curl -s -X POST http://localhost:8000/chat/groq/simple ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"Hóa đơn nào có tổng tiền cao nhất?\", \"user_id\": \"test\"}" | jq .

REM ============ TEST 4: Streaming Chat ============
REM Chat streaming (real-time chunks)
curl -s -X POST http://localhost:8000/chat/groq/stream ^
  -H "Content-Type: application/json" ^
  -d "{\"message\": \"Có bao nhiêu hóa đơn?\", \"user_id\": \"test\"}"

REM ============ TEST 5: Get Invoices ============
REM Lấy danh sách hóa đơn
curl -s -X POST http://localhost:8000/api/invoices/list ^
  -H "Content-Type: application/json" ^
  -d "{\"limit\": 10}" | jq .invoices

REM ============ TEST 6: Statistics ============
REM Thống kê hóa đơn
curl -s http://localhost:8000/api/groq/tools/get_statistics | jq .

REM ============ TEST 7: Upload Image ============
REM Upload ảnh để test OCR
curl -X POST http://localhost:8000/upload-image ^
  -F "image=@C:\path\to\invoice.jpg" ^
  -F "user_id=test_user" | jq .

REM ============ TEST 8: Check Job Status ============
REM Kiểm tra trạng thái OCR job (thay JOB_ID bằng job ID từ test 7)
curl -s http://localhost:8000/api/ocr/job/JOB_ID | jq .
