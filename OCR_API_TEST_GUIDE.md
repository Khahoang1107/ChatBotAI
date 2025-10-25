# 🧪 OCR API Test Guide

## Nhanh chóng

### 1️⃣ Start Backend Server

```powershell
cd f:\DoAnCN\backend
python -m uvicorn main:app --host localhost --port 8000
```

### 2️⃣ Run Python Tests (Comprehensive)

```powershell
cd f:\DoAnCN
python test_ocr_api.py
```

### 3️⃣ Run CURL Tests (Quick)

```powershell
cd f:\DoAnCN
powershell -ExecutionPolicy Bypass -File test_ocr_curl.ps1
```

---

## 📋 Chi tiết các Test

### Test 1: Health Check

**Kiểm tra:** Server có running không?

```bash
GET http://localhost:8000/health
```

**Kết quả mong muốn:**

```json
{
  "status": "ok",
  "timestamp": "2025-10-22T..."
}
```

---

### Test 2: Groq Tools

**Kiểm tra:** Danh sách 7 tools database có sẵn không?

```bash
GET http://localhost:8000/api/groq/tools
```

**Kết quả mong muốn:**

```json
{
  "tools": [
    {
      "name": "get_all_invoices",
      "description": "Get all invoices from database"
    },
    ...
  ]
}
```

---

### Test 3: Simple Chat (Blocking)

**Kiểm tra:** Chat endpoint không có streaming (chặn cho đến hết response)

```bash
POST http://localhost:8000/chat/groq/simple
Content-Type: application/json

{
  "message": "Hóa đơn nào có tổng tiền cao nhất?",
  "user_id": "test_user"
}
```

**Kết quả mong muốn:**

```json
{
  "message": "Hóa đơn INV-2025-001 có tổng tiền cao nhất: 5,000,000 VND",
  "type": "text",
  "method": "groq_simple",
  "timestamp": "2025-10-22T...",
  "user_id": "test_user"
}
```

**⏱️ Thời gian:** 2-5 giây (chờ Groq API response)

---

### Test 4: Streaming Chat (Real-time) ⭐ NEW

**Kiểm tra:** Chat endpoint với streaming (chunks real-time)

```bash
POST http://localhost:8000/chat/groq/stream
Content-Type: application/json

{
  "message": "Hóa đơn nào có tổng tiền cao nhất?",
  "user_id": "test_user"
}
```

**Kết quả mong muốn (NDJSON format):**

```
{"type": "content", "text": "Hóa", "timestamp": "..."}
{"type": "content", "text": " đơn", "timestamp": "..."}
{"type": "content", "text": " INV-2025-001", "timestamp": "..."}
...
{"type": "done", "timestamp": "..."}
```

**Ưu điểm:**

- ✅ Hiển thị response từng chunk
- ✅ Cải thiện UX (không chờ hết)
- ✅ Tương thích frontend streaming

---

### Test 5: Get Invoices List

**Kiểm tra:** Lấy danh sách hóa đơn từ database

```bash
POST http://localhost:8000/api/invoices/list
Content-Type: application/json

{
  "limit": 10
}
```

**Kết quả mong muốn:**

```json
{
  "success": true,
  "invoices": [
    {
      "id": 1,
      "invoice_code": "INV-2025-001",
      "invoice_type": "general",
      "buyer_name": "CÔNG TY ABC",
      "seller_name": "CÔNG TY XYZ",
      "total_amount": "5,000,000",
      "confidence_score": 0.95,
      "created_at": "2025-10-22T..."
    }
  ]
}
```

---

### Test 6: Get Statistics

**Kiểm tra:** Thống kê tổng hợp hóa đơn

```bash
GET http://localhost:8000/api/groq/tools/get_statistics
```

**Kết quả mong muốn:**

```json
{
  "total_invoices": 3,
  "total_amount": 15000000,
  "average_amount": 5000000,
  "invoice_types": {
    "general": 3
  }
}
```

---

## 🔄 Full Workflow Test

### Bước 1: Upload Ảnh

```bash
POST http://localhost:8000/upload-image
Content-Type: multipart/form-data

- image: <binary file>
- user_id: test_user
```

**Response:**

```json
{
  "success": true,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "File uploaded! Processing in background..."
}
```

### Bước 2: Check Job Status (Poll)

```bash
GET http://localhost:8000/api/ocr/job/550e8400-e29b-41d4-a716-446655440000
```

**Response (while processing):**

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 50
}
```

**Response (when done):**

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "done",
  "progress": 100,
  "invoice_id": 42
}
```

### Bước 3: Chat về Ảnh

```bash
POST http://localhost:8000/chat/groq/stream
Content-Type: application/json

{
  "message": "Chi tiết hóa đơn này là gì?",
  "user_id": "test_user"
}
```

---

## 📊 Endpoints Overview

| Endpoint                         | Method | Purpose                            |
| -------------------------------- | ------ | ---------------------------------- |
| `/health`                        | GET    | Health check                       |
| `/chat/groq`                     | POST   | Chat (blocking, with tools)        |
| `/chat/groq/simple`              | POST   | Chat (blocking, no tools)          |
| `/chat/groq/stream`              | POST   | Chat (streaming, real-time) ⭐ NEW |
| `/api/groq/tools`                | GET    | List all tools                     |
| `/api/groq/tools/get_statistics` | GET    | Get statistics                     |
| `/upload-image`                  | POST   | Upload image & enqueue OCR         |
| `/api/ocr/enqueue`               | POST   | Enqueue OCR job manually           |
| `/api/ocr/job/{job_id}`          | GET    | Check job status                   |
| `/api/invoices/list`             | POST   | Get invoices                       |

---

## 🐛 Troubleshooting

### Backend Connection Error

```
ConnectionRefusedError: [WinError 10061]
```

**Solution:** Start backend first

```powershell
cd f:\DoAnCN\backend
python -m uvicorn main:app --host localhost --port 8000
```

### Streaming Not Working

**Check:**

1. Frontend connects to `http://localhost:8000/chat/groq/stream`
2. Backend returns `media_type: "application/x-ndjson"`
3. Frontend parses chunks line-by-line

**Debug:** Check browser DevTools Network tab - should see streaming response

### OCR Job Still "queued"

**Check:**

1. Worker process running: `python worker.py`
2. Database connection working
3. Upload folder exists: `f:\DoAnCN\backend\uploads\`

---

## 📈 Performance Metrics

| Operation        | Time   | Note                |
| ---------------- | ------ | ------------------- |
| Upload image     | ~50ms  | Returns immediately |
| OCR processing   | 2-5s   | Background          |
| Chat (blocking)  | 2-5s   | Waits for Groq      |
| Chat (streaming) | 2-5s   | Shows chunks        |
| Get invoices     | ~100ms | DB query            |
| Health check     | ~10ms  | Instant             |

---

## 🎯 Next Steps

1. ✅ Start backend server
2. ✅ Run Python tests: `python test_ocr_api.py`
3. ✅ Or run curl tests: `powershell -File test_ocr_curl.ps1`
4. ✅ Test frontend integration (React)
5. ✅ Check streaming UX in browser

---

## 📞 Support

**Common Issues:**

**Q: Streaming không hiển thị từng chữ?**
A: Check frontend `ChatBot.tsx` - phải dùng `fetch().body.getReader()` để parse NDJSON

**Q: Chat trả lời sai dữ liệu?**
A: Groq tools có 7 functions để query DB, verify database có invoices

**Q: Upload ảnh không lưu?**
A: Check `uploads/` folder exist, permissions OK, database connected

---

Generated: 2025-10-22
Version: 1.0
