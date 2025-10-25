# 📚 Complete Test Suite Documentation

## 🎯 Overview

Bạn vừa nhận được **5 test files** cho OCR API:

| #   | File                    | Purpose                               | Run Time |
| --- | ----------------------- | ------------------------------------- | -------- |
| 1️⃣  | `quick_test.py`         | Start here! 6 basic tests             | 5-10s    |
| 2️⃣  | `test_ocr_api.py`       | Full comprehensive suite              | 30-60s   |
| 3️⃣  | `test_ocr_curl.ps1`     | PowerShell tests (no Python needed)   | 10s      |
| 4️⃣  | `test_commands.bat`     | Individual curl commands (copy/paste) | Variable |
| 5️⃣  | `OCR_API_TEST_GUIDE.md` | Detailed technical guide              | N/A      |

---

## 🚀 Step-by-Step Guide

### Stage 1: Setup (2 minutes)

```powershell
# Terminal 1: Start backend server
cd f:\DoAnCN\backend
python -m uvicorn main:app --host localhost --port 8000

# Wait for output:
# INFO:     Uvicorn running on http://localhost:8000
```

### Stage 2: Quick Verification (1 minute)

```powershell
# Terminal 2: Run quick test
cd f:\DoAnCN
python quick_test.py

# Expected output: ✅ All quick tests passed!
```

### Stage 3: Full Test (1-2 minutes)

```powershell
# Terminal 2: Run comprehensive test
python test_ocr_api.py

# Shows: OCR upload, job processing, streaming, etc.
```

### Stage 4: Individual API Tests

```powershell
# Test specific endpoints using curl
curl http://localhost:8000/health
curl http://localhost:8000/api/groq/tools
curl -X POST http://localhost:8000/chat/groq/simple `
  -H "Content-Type: application/json" `
  -d "{\"message\": \"Hello\"}"
```

---

## 📋 What Each Test Does

### quick_test.py - ⚡ Perfect for First Time

```python
python quick_test.py
```

**Tests:**

```
1️⃣  Health Check .......................... Server responding?
2️⃣  Get Groq Tools ....................... 7 database tools available?
3️⃣  Get Invoices ......................... Data in database?
4️⃣  Chat - Blocking ...................... Simple response works?
5️⃣  Chat - Streaming ..................... New feature: real-time chunks?
6️⃣  Invoice Statistics ................... Stats accurate?
```

**Time:** 5-10 seconds
**Difficulty:** ⭐ Easy

---

### test_ocr_api.py - 🔬 Full Validation

```python
python test_ocr_api.py
```

**Tests:**

```
1️⃣  Health Check
2️⃣  Upload Image (creates fake invoice automatically)
3️⃣  Enqueue OCR Job
4️⃣  Poll Job Status (waits up to 30 seconds for completion)
5️⃣  Get Invoices List
6️⃣  Streaming Chat
```

**Features:**

- Auto-generates test image with invoice text
- Shows real-time polling progress
- Color-coded output
- Handles timeouts gracefully

**Time:** 30-60 seconds
**Difficulty:** ⭐⭐ Intermediate

---

### test_ocr_curl.ps1 - 📝 PowerShell Version

```powershell
powershell -ExecutionPolicy Bypass -File test_ocr_curl.ps1
```

**Tests:**

```
1️⃣  Health Check
2️⃣  Groq Tools
3️⃣  Simple Chat
4️⃣  Streaming Chat
5️⃣  Invoices List
6️⃣  Statistics
```

**Time:** ~10 seconds
**Difficulty:** ⭐ Easy
**Advantage:** No Python needed!

---

### test_commands.bat - 💻 Manual Commands

Copy/paste individual commands for specific tests:

```bat
# Health check
curl -s http://localhost:8000/health | jq .

# Chat test
curl -s -X POST http://localhost:8000/chat/groq/simple `
  -H "Content-Type: application/json" `
  -d "{\"message\": \"Hóa đơn?\", \"user_id\": \"test\"}" | jq .

# Upload image
curl -X POST http://localhost:8000/upload-image `
  -F "image=@invoice.jpg" `
  -F "user_id=test_user" | jq .
```

**Time:** Variable
**Difficulty:** ⭐⭐ Manual

---

## 🌊 New Feature: Streaming Chat

### What is Streaming?

**Old (Blocking):**

```
User: "Hello?"
[waiting 3 seconds...]
Bot: "This is a complete response."
```

**New (Streaming):**

```
User: "Hello?"
Bot: "This" → "is" → "a" → "complete" → "response."
(shows in real-time, word by word)
```

### Test It

```powershell
# Endpoint
POST http://localhost:8000/chat/groq/stream

# Request
{
  "message": "Hóa đơn nào có tổng tiền cao nhất?",
  "user_id": "test"
}

# Response (NDJSON format - one JSON per line)
{"type": "content", "text": "Hóa"}
{"type": "content", "text": " đơn"}
{"type": "content", "text": " INV-2025-001"}
...
{"type": "done"}
```

### Run Test

```powershell
# Python
python test_ocr_api.py  # TEST 6

# PowerShell
powershell -File test_ocr_curl.ps1  # TEST 4

# Manual curl
curl -X POST http://localhost:8000/chat/groq/stream `
  -H "Content-Type: application/json" `
  -d "{\"message\": \"Chi tiết?\", \"user_id\": \"test\"}"
```

---

## 📊 API Endpoints Being Tested

| Endpoint                         | Method | Status                |
| -------------------------------- | ------ | --------------------- |
| `/health`                        | GET    | ✅ Health check       |
| `/api/groq/tools`                | GET    | ✅ List 7 tools       |
| `/chat/groq/simple`              | POST   | ✅ Blocking chat      |
| `/chat/groq/stream`              | POST   | ✅ **NEW: Streaming** |
| `/api/invoices/list`             | POST   | ✅ Get invoices       |
| `/api/groq/tools/get_statistics` | GET    | ✅ Statistics         |
| `/upload-image`                  | POST   | ✅ Upload & enqueue   |
| `/api/ocr/job/{id}`              | GET    | ✅ Check status       |

---

## ✅ Success Criteria

After running tests, verify:

```
✅ quick_test.py:
  - All 6 tests pass
  - No connection errors

✅ test_ocr_api.py:
  - Creates fake invoice image
  - Uploads successfully
  - Job status polls correctly
  - Streaming shows chunks

✅ Browser test:
  - Frontend connects to port 8000
  - Chat streaming shows real-time
  - Messages appear incrementally
```

---

## 🐛 Common Issues & Fixes

### Issue: ConnectionRefusedError

```
ConnectionRefusedError: [WinError 10061]
```

**Fix:** Start backend in different terminal

```powershell
cd f:\DoAnCN\backend
python -m uvicorn main:app --host localhost --port 8000
```

### Issue: ModuleNotFoundError

```
ModuleNotFoundError: No module named 'requests'
```

**Fix:** Install dependencies

```powershell
pip install requests pillow
```

### Issue: jq not found

```
'jq' is not recognized
```

**Fix:** Skip jq or install

```powershell
choco install jq
# Or just remove " | jq ." from curl commands
```

### Issue: Streaming shows empty

Check frontend `ChatBot.tsx`:

```typescript
// Should use:
const reader = response.body.getReader();

// NOT:
const data = await response.json();
```

---

## 📈 Expected Performance

| Operation      | Time  | Pass/Fail |
| -------------- | ----- | --------- |
| Health check   | ~10ms | ✅ <100ms |
| Get tools      | ~50ms | ✅ <100ms |
| Simple chat    | 2-5s  | ✅ <10s   |
| Streaming chat | 2-5s  | ✅ <10s   |
| Upload         | ~50ms | ✅ <100ms |
| OCR process    | 2-5s  | ✅ <10s   |

---

## 🎓 Learning Path

**Beginner:**

1. Run `quick_test.py`
2. Read output
3. Verify ✅

**Intermediate:**

1. Run `test_ocr_api.py`
2. Watch OCR job process
3. Understand workflow

**Advanced:**

1. Modify `test_ocr_api.py`
2. Add custom tests
3. Test edge cases

---

## 📞 Command Reference

```powershell
# Quick start (2 lines)
cd f:\DoAnCN\backend && python -m uvicorn main:app --host localhost --port 8000
# (New terminal)
cd f:\DoAnCN && python quick_test.py

# Full test
python test_ocr_api.py

# PowerShell test
powershell -ExecutionPolicy Bypass -File test_ocr_curl.ps1

# Individual tests
curl http://localhost:8000/health
curl http://localhost:8000/api/groq/tools
curl -X POST http://localhost:8000/chat/groq/simple -H "Content-Type: application/json" -d "{\"message\": \"test\"}"
```

---

## 🚀 Next Steps

After tests pass:

1. ✅ Test frontend integration
2. ✅ Verify streaming in browser
3. ✅ Test OCR workflow
4. ✅ Upload real invoice images
5. ✅ Production deployment

---

## 📖 Documentation Files

| File                      | Purpose                            |
| ------------------------- | ---------------------------------- |
| `OCR_API_TEST_GUIDE.md`   | Technical guide with detailed info |
| `TEST_FILES_REFERENCE.md` | Comparison & reference             |
| `test_ocr_api.py`         | Full test code                     |
| `quick_test.py`           | Simple test code                   |
| `test_ocr_curl.ps1`       | PowerShell commands                |

---

**Created:** 2025-10-22
**Version:** 1.0
**Status:** ✅ Ready to test

Now run: `python quick_test.py` 🚀
