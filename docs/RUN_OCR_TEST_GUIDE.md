# 🚀 OCR End-to-End Test - Hướng Dẫn Nhanh

## 📌 Mục tiêu

Upload ảnh hóa đơn → OCR xử lý → Lưu vào database → Hiển thị chi tiết → AI phân tích

## 🎯 Các Bước

### Step 1: Đặt ảnh vào thư mục

```
f:\DoAnCN\
└── z7079279178506_8cd2d5ce4446c8e94ffd081080adb5bf.jpg
```

### Step 2: Start Backend (Terminal 1)

```powershell
cd f:\DoAnCN\backend
python -m uvicorn main:app --host localhost --port 8000
```

Chờ thấy:

```
INFO:     Uvicorn running on http://localhost:8000
```

### Step 3: Start OCR Worker (Terminal 2)

```powershell
cd f:\DoAnCN\backend
python worker.py
```

Chờ thấy:

```
✅ OCR Worker initialized and running
```

### Step 4: Run OCR Test (Terminal 3)

```powershell
cd f:\DoAnCN
python run_ocr_test.py
```

## ✅ Expected Output

```
1️⃣ Health Check
✅ Server running on localhost:8000

2️⃣ Looking for image to upload...
✅ Found image: z7079279178506_8cd2d5ce4446c8e94ffd081080adb5bf.jpg

3️⃣ Uploading image (39.5KB)...
✅ Upload successful!
   Job ID: 550e8400-e29b-41d4-a716-446655440000
   Status: queued

4️⃣ Waiting for OCR processing...
   [2.5s] Status: processing     | Progress: 50%
   [5.2s] Status: done           | Progress: 100%
✅ OCR completed!
   Invoice ID: 42

5️⃣ Retrieving saved invoice from database...
✅ Found invoice in database!

📄 Invoice Details:
   • ID: 42
   • Code: INV-2025-001
   • Type: general
   • Buyer: CÔNG TY ABC
   • Seller: CÔNG TY XYZ
   • Amount: 5,000,000
   • Confidence: 94.50%

6️⃣ Asking Groq AI about the invoice...
✅ AI Response:

Hóa đơn INV-2025-001 là loại hóa đơn chung...

🎉 OCR END-TO-END TEST COMPLETE!
```

## 🔧 Troubleshooting

### Backend không start?

```
cd f:\DoAnCN\backend
python -m uvicorn main:app --host localhost --port 8000
```

### Worker không start?

```
cd f:\DoAnCN\backend
python worker.py
```

Nếu lỗi:

```
pip install pytesseract pillow psycopg2-binary
```

### Test lỗi "Cannot connect"?

- Kiểm tra backend running trên port 8000
- Kiểm tra PostgreSQL chạy
- Kiểm tra file ảnh có sẵn

### OCR timeout (>30s)?

- Worker chưa xử lý
- Tesseract chưa cài
- Kiểm tra logs của worker

## 📊 Workflow

```
[You]
  ↓ Upload ảnh
[Frontend]
  ↓ POST /upload-image
[Backend:8000]
  ↓ Save file + Enqueue job
[Database: ocr_jobs]
  ↓ Status: queued
[Worker]
  ↓ Poll & Process (Tesseract OCR)
[Worker]
  ↓ Extract fields & Save to invoices
[Database: invoices]
  ↓ Status: done + invoice_id
[test script]
  ↓ Poll status & Retrieve invoice
[Display]
  ↓ Show invoice details
[Groq AI]
  ↓ Analyze & respond
```

## 🎯 Success Criteria

- ✅ Upload returns job_id immediately
- ✅ Job status changes from queued → processing → done
- ✅ Invoice saved to database with proper fields
- ✅ Groq AI can analyze the invoice
- ✅ Full workflow < 30 seconds

## 📞 Commands Summary

```powershell
# Terminal 1: Backend
cd f:\DoAnCN\backend && python -m uvicorn main:app --host localhost --port 8000

# Terminal 2: Worker
cd f:\DoAnCN\backend && python worker.py

# Terminal 3: Test
cd f:\DoAnCN && python run_ocr_test.py
```

---

**Status:** ✅ READY
**Date:** October 22, 2025
