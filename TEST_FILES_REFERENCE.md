# 🧪 OCR API Test Files - Complete Reference

## 📁 File Structure

```
f:\DoAnCN\
├── test_ocr_api.py          ⭐ Full test suite (Python)
├── test_ocr_curl.ps1        📝 PowerShell curl commands
├── quick_test.py            ⚡ Quick 6 tests (fastest)
├── test_commands.bat        💻 Batch curl commands
├── OCR_API_TEST_GUIDE.md    📖 Detailed guide (this file)
└── test_streaming.py        (Previous streaming test)
```

---

## 🚀 Quick Start (5 minutes)

### Step 1: Start Backend

```powershell
cd f:\DoAnCN\backend
python -m uvicorn main:app --host localhost --port 8000
```

**Output mong muốn:**

```
INFO:     Uvicorn running on http://localhost:8000 (Press CTRL+C to quit)
```

### Step 2: Open New Terminal & Run Quick Test

```powershell
cd f:\DoAnCN
python quick_test.py
```

**Output:**

```
======================================================================
✅ QUICK OCR API TEST
======================================================================

1️⃣  Health Check
----------------------------------------------------------------------
✅ Server OK: 200

2️⃣  Get Groq Tools
----------------------------------------------------------------------
✅ Found 7 tools:
   • get_all_invoices
   • search_invoices
   • ... etc
```

---

## 📊 Test Files Comparison

| File                | Type       | Tests      | Duration   | Best For            |
| ------------------- | ---------- | ---------- | ---------- | ------------------- |
| `quick_test.py`     | Python     | 6 tests    | 5-10s      | 🚀 Getting started  |
| `test_ocr_api.py`   | Python     | 6 advanced | 30-60s     | 🔬 Comprehensive    |
| `test_ocr_curl.ps1` | PowerShell | 6 tests    | 10s        | 🔧 Manual testing   |
| `test_commands.bat` | Batch      | 8 commands | Copy/paste | 💻 Individual tests |
| `test_streaming.py` | Python     | 2 tests    | 10-15s     | 🌊 Streaming only   |

---

## 📋 Each Test File Explained

### 1️⃣ `quick_test.py` - ⚡ FASTEST & EASIEST

**Khi nào dùng:** Lần đầu test, verify server alive, check API quickly

**Cách chạy:**

```powershell
python quick_test.py
```

**Gì được test:**

1. ✅ Health check
2. ✅ Groq tools list
3. ✅ Invoices from DB
4. ✅ Simple chat (blocking)
5. ✅ Streaming chat (new!)
6. ✅ Statistics

**Kết quả:** ~20 lines output, 5-10 seconds

---

### 2️⃣ `test_ocr_api.py` - 🔬 COMPREHENSIVE

**Khi nào dùng:** Full validation, OCR workflow test, detailed debugging

**Cách chạy:**

```powershell
python test_ocr_api.py
```

**Gì được test:**

1. Health check
2. Upload image (creates test image automatically)
3. Enqueue OCR job
4. Poll job status with timeout (waits up to 30s for OCR completion)
5. Get invoices list
6. Streaming chat

**Bonus:**

- Automatically creates fake invoice image
- Shows real-time polling progress
- Handles timeouts gracefully
- Color output for easy reading

**Kết quả:** Detailed output with all steps, 30-60 seconds

---

### 3️⃣ `test_ocr_curl.ps1` - 📝 POWERSHELL CURL

**Khi nào dùng:** Manual testing, no Python dependencies, run in PowerShell

**Cách chạy:**

```powershell
powershell -ExecutionPolicy Bypass -File test_ocr_curl.ps1
```

**Gì được test:**

1. Health check
2. Groq tools
3. Simple chat
4. Streaming chat (shows chunks)
5. Invoices list
6. Statistics

**Ưu điểm:**

- 🎯 Không cần Python, chỉ PowerShell
- 📊 Định dạng output dễ đọc
- 🔄 Có thể sửa dễ dàng

---

### 4️⃣ `test_commands.bat` - 💻 INDIVIDUAL CURL COMMANDS

**Khi nào dùng:** Test một endpoint cụ thể, debug issue, copy/paste commands

**Cách dùng:**
Mở file, copy từng command vào PowerShell

```powershell
# Ví dụ: Test health check
curl -s http://localhost:8000/health | jq .

# Ví dụ: Upload image (thay path)
curl -X POST http://localhost:8000/upload-image `
  -F "image=@C:\path\to\invoice.jpg" `
  -F "user_id=test_user" | jq .
```

**8 Commands Available:**

1. Health check
2. Get tools
3. Simple chat
4. Streaming chat
5. Get invoices
6. Statistics
7. Upload image
8. Check job status

---

### 5️⃣ `test_streaming.py` - 🌊 STREAMING ONLY

**Khi nào dùng:** Test streaming endpoint specifically, debug stream parsing

**Cách chạy:**

```powershell
python test_streaming.py
```

**Tests:**

1. Blocking endpoint (old style)
2. Streaming endpoint (new style)

**Output:** Detailed chunk-by-chunk analysis

---

## 🔄 Complete Workflow Test

### Scenario: Upload → Process → Chat

```powershell
# 1. Start backend
cd f:\DoAnCN\backend
python -m uvicorn main:app --host localhost --port 8000

# 2. In new terminal, run quick test
cd f:\DoAnCN
python quick_test.py

# 3. Or test upload + OCR manually
# Upload image
curl -X POST http://localhost:8000/upload-image `
  -F "image=@invoice.jpg" `
  -F "user_id=test_user"

# Get job_id from response, then poll status
curl http://localhost:8000/api/ocr/job/{job_id}

# Once done, chat about it
curl -X POST http://localhost:8000/chat/groq/stream `
  -H "Content-Type: application/json" `
  -d "{\"message\": \"Chi tiết hóa đơn này?\", \"user_id\": \"test\"}"
```

---

## ✅ Expected Outputs

### 1. Health Check

```json
{
  "status": "ok"
}
```

### 2. Groq Tools

```json
{
  "tools": [
    {
      "name": "get_all_invoices",
      "description": "Get all invoices from database with limit"
    },
    ...
  ]
}
```

### 3. Simple Chat

```json
{
  "message": "Hóa đơn INV-2025-001 có tổng tiền cao nhất là 5,000,000 VND",
  "type": "text",
  "method": "groq_simple"
}
```

### 4. Streaming Chat (NDJSON)

```
{"type": "content", "text": "Hóa", "timestamp": "..."}
{"type": "content", "text": " đơn", "timestamp": "..."}
...
{"type": "done", "timestamp": "..."}
```

### 5. Invoices List

```json
{
  "success": true,
  "invoices": [
    {
      "id": 1,
      "invoice_code": "INV-2025-001",
      "invoice_type": "general",
      "buyer_name": "CÔNG TY ABC",
      "total_amount": "5,000,000"
    }
  ]
}
```

---

## 🐛 Troubleshooting

| Issue                      | Solution                                         |
| -------------------------- | ------------------------------------------------ |
| `ConnectionRefusedError`   | Start backend: `python -m uvicorn main:app ...`  |
| `jq not found`             | Install: `choco install jq` (or skip jq piping)  |
| `No module named requests` | Install: `pip install requests pillow`           |
| `ModuleNotFoundError: PIL` | Install: `pip install Pillow`                    |
| Streaming no chunks        | Check frontend `ChatBot.tsx` using `getReader()` |

---

## 📈 Performance Expectations

| Operation      | Expected Time | Note                   |
| -------------- | ------------- | ---------------------- |
| Health check   | ~10ms         | Instant                |
| Get tools      | ~50ms         | Simple query           |
| Simple chat    | 2-5s          | Waits for Groq API     |
| Streaming chat | 2-5s          | Same, but shows chunks |
| Upload image   | ~50ms         | File save + enqueue    |
| OCR processing | 2-5s          | Background (worker)    |
| Get invoices   | ~100ms        | DB query               |

---

## 🎯 Test Checklist

Before deploying, verify:

- [ ] Backend starts without errors
- [ ] Health check returns 200
- [ ] Tools endpoint returns 7 tools
- [ ] Chat returns intelligent response
- [ ] Streaming returns NDJSON chunks
- [ ] Invoices list shows data
- [ ] Statistics accurate
- [ ] Upload enqueues job
- [ ] Job status updates
- [ ] OCR processes successfully
- [ ] Frontend can fetch streaming

---

## 🚀 Next Steps

1. ✅ Run `python quick_test.py`
2. ✅ If all pass, run `python test_ocr_api.py`
3. ✅ Test frontend streaming integration
4. ✅ Test OCR workflow end-to-end
5. ✅ Deploy to production

---

## 📞 Quick Command Reference

```powershell
# Start backend
cd f:\DoAnCN\backend && python -m uvicorn main:app --host localhost --port 8000

# Quick test
cd f:\DoAnCN && python quick_test.py

# Full test
python test_ocr_api.py

# PowerShell test
powershell -ExecutionPolicy Bypass -File test_ocr_curl.ps1

# Individual tests
curl http://localhost:8000/health
curl http://localhost:8000/api/groq/tools
curl -X POST http://localhost:8000/chat/groq/simple -H "Content-Type: application/json" -d "{\"message\": \"Hóa đơn nào có tổng tiền cao nhất?\"}"
```

---

Generated: 2025-10-22
Version: 2.0
