# 🧪 OCR Upload → Database Test

## Mục tiêu

Kiểm tra **End-to-End**: Upload ảnh → OCR xử lý → Lưu vào database → Lấy dữ liệu

## 📋 Test Checklist

- [ ] Backend running (:8000)
- [ ] PostgreSQL running
- [ ] OCR worker running
- [ ] Test image available
- [ ] Run test script
- [ ] Verify invoice in database
- [ ] Query Groq about invoice

## 🚀 Chạy Test

### Step 1: Start Backend (Terminal 1)

```powershell
cd f:\DoAnCN\backend
uvicorn main:app --host localhost --port 8000
```

Wait for:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 2: Start OCR Worker (Terminal 2)

```powershell
cd f:\DoAnCN\backend
python worker.py
```

Wait for:

```
🔄 Worker started - polling every 5s for up to 3 jobs
```

### Step 3: Run Test Script (Terminal 3)

```powershell
cd f:\DoAnCN
python test_ocr_upload_to_db.py
```

## 📊 Expected Output

```
======================================================================
🧪 OCR UPLOAD → DATABASE TEST
======================================================================

1️⃣ Check Server...
✅ Backend running on :8000

2️⃣ Checking Invoices BEFORE Upload...
   📊 Total invoices in DB: 3
   • Last invoice: INV-2025-003 (Cửa hàng ABC)

3️⃣ Looking for Test Image...
   ✅ Found: test_invoice.jpg (12.9KB)

4️⃣ Uploading Image...
   ✅ Upload successful!
   📋 Job ID: 550e8400-e29b-41d4-a716-446655440000
   📊 Status: queued
   ⏱️  Server response time: <100ms

5️⃣ Waiting for OCR Processing...
   (Polling every 2 seconds, max 60 seconds)
   ⏱️  [27.3s] Status: done           | Progress: 100%
   ✅ OCR Complete! Invoice ID: 4

6️⃣ Verifying Invoice in Database...
   📊 Invoices before: 3
   📊 Invoices after:  4
   ✅ Difference: +1 new invoice(s)

   ✅ New invoice found in database!

   📄 Invoice Details:
      • ID: 4
      • Code: INV-UNKNOWN
      • Type: general
      • Buyer: Unknown
      • Seller: Unknown
      • Amount: 0 VND
      • Confidence: 0.00%
      • File: test_invoice.jpg
      • Date: 23/10/2025

7️⃣ Asking Groq AI About the Invoice...
   ✅ Groq responded!

   🤖 AI Response (first 300 chars):
      Hóa đơn ID 4 đã được lưu vào hệ thống. Tôi sẽ lấy thông tin
      chi tiết về hóa đơn này bằng cách gọi tool get_invoice_by_id...

======================================================================
✅ TEST COMPLETE - RESULTS SUMMARY
======================================================================

📊 UPLOAD TEST:
   ✅ Image uploaded successfully
   ✅ Job ID created: 550e8400-e29b-41d4-a716-446655440000

⏱️  OCR PROCESSING:
   ✅ OCR completed (Invoice ID: 4)
   ✅ Processing time: 27.3s

💾 DATABASE SAVE:
   ✅ Invoice saved to database
   ✅ Invoice count: 3 → 4
   ✅ New invoice ID: 4

🤖 GROQ INTEGRATION:
   ✅ Can query Groq about uploaded invoice

🎉 TEST STATUS: SUCCESS!
   Upload → OCR → Save → Query workflow is WORKING! ✨

======================================================================
```

## ✅ Success Criteria

### ✅ PASS

- [ ] Job created (status: queued)
- [ ] OCR processing starts (status: processing)
- [ ] OCR completes (status: done)
- [ ] Invoice ID returned
- [ ] Invoice count increases in DB
- [ ] New invoice visible in database
- [ ] Groq can query the invoice

### ❌ FAIL Scenarios

**Scenario 1: Job stuck at "queued"**

```
⏱️  [30.0s] Status: queued | Progress: 0%
❌ Timeout (>60s)
```

**Fix**: Start OCR worker

```powershell
cd f:\DoAnCN\backend
python worker.py
```

**Scenario 2: OCR failed**

```
❌ OCR Failed: Tesseract OCR failed or is not installed
```

**Fix**: Install Tesseract

```powershell
# Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
# Then add to PATH
```

**Scenario 3: Database not saving**

```
Invoice ID 4 not found in list
```

**Fix**: Check database connection

```powershell
# Check PostgreSQL
psql -U postgres -d ocr_database_new -c "SELECT COUNT(*) FROM invoices"
```

**Scenario 4: Groq failing**

```
⚠️  Groq chat failed: 500
```

**Fix**: Check GROQ_API_KEY

```powershell
$env:GROQ_API_KEY = "your-api-key-here"
```

## 📊 Database Queries

### Check invoices

```sql
SELECT id, invoice_code, buyer_name, confidence_score
FROM invoices
ORDER BY created_at DESC LIMIT 5;
```

### Check OCR jobs

```sql
SELECT id, status, progress, invoice_id
FROM ocr_jobs
ORDER BY created_at DESC LIMIT 5;
```

### Check recently saved invoices

```sql
SELECT * FROM invoices
WHERE created_at > NOW() - INTERVAL '1 hour'
ORDER BY created_at DESC;
```

## 🔧 Troubleshooting

### Backend not responding

```
❌ Cannot connect to backend
```

**Solution**: Start backend

```powershell
cd f:\DoAnCN\backend
uvicorn main:app --host localhost --port 8000
```

### No test image

```
❌ No JPG image found
```

**Solution**:

- Upload test_invoice.jpg to f:\DoAnCN\
- Or download sample from uploads/

### OCR timeout

```
❌ Timeout (>60s)
```

**Possible causes**:

1. Worker not running
2. Tesseract too slow
3. Database locked

**Solution**:

```powershell
# Check worker logs
cd f:\DoAnCN\backend && python worker.py

# Or increase timeout in test
# Change: while time.time() - start_time < 60:
#     To: while time.time() - start_time < 120:
```

## 📝 What Gets Tested

| Component  | Test                      | Status |
| ---------- | ------------------------- | ------ |
| Upload API | POST /upload-image        | ✅     |
| Job Queue  | OCR job created           | ✅     |
| OCR Worker | Tesseract processes image | ✅     |
| Database   | Invoice saved             | ✅     |
| API Query  | Get invoices list         | ✅     |
| Groq AI    | Query about invoice       | ✅     |

## 🎯 Full Workflow

```
User
  ↓ (Upload image)
Frontend
  ↓ (POST /upload-image)
Backend:8000
  ├─ Save file to /uploads/
  └─ Enqueue job → return job_id ✅

User Polls Status (optional)
  ↓ (GET /api/ocr/job/{job_id})
Backend:8000
  ├─ status: queued → processing → done ✅

Worker (Background)
  ├─ Poll ocr_jobs
  ├─ Run Tesseract OCR
  ├─ Extract fields
  └─ Save to invoices table ✅

User Queries Invoice
  ↓ (POST /chat/groq)
Groq LLM
  ├─ Call get_all_invoices()
  ├─ Call get_invoice_by_id(4)
  └─ Return intelligent response ✅
```

## 📞 Need Help?

1. Check logs: `tail -f backend_logs.txt`
2. Test health: `curl http://localhost:8000/health`
3. Test upload: `python quick_test.py`
4. Test DB: `psql -U postgres -d ocr_database_new`
5. Test Groq: `python test_groq_function_calling.py`

## 📚 Related Files

- `test_ocr_upload_to_db.py` - This test script
- `backend/worker.py` - OCR processor
- `backend/main.py` - FastAPI endpoints
- `backend/groq_tools.py` - Groq integration
- `GROQ_FUNCTION_CALLING_SUCCESS.md` - Groq docs

---

**Last Updated**: October 23, 2025
**Status**: ✅ READY
