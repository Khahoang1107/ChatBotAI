# Async OCR Pipeline Architecture (Current Implementation)

## 🎯 System Overview (FastAPI Unified - v2.1)

```
┌─────────────────────────────────────────────────────────────────────┐
│                      INVOICE PROCESSING SYSTEM                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Frontend (React)                                                   │
│      ↓ upload image / chat                                         │
│  ┌─────────────────────────────────────────────────────┐           │
│  │ FastAPI Backend (Unified) :8000 ✨                 │           │
│  │ ├─ POST /chat (Groq LLM)                           │           │
│  │ ├─ POST /chat/simple                               │           │
│  │ ├─ POST /upload-image                              │           │
│  │ │  └─ Save file → uploads/                         │           │
│  │ │  └─ Enqueue job → return job_id (FAST 50ms)     │           │
│  │ ├─ POST /api/ocr/enqueue                           │           │
│  │ │  └─ Create job record in ocr_jobs DB             │           │
│  │ ├─ GET /api/ocr/job/{job_id}                       │           │
│  │ │  └─ Return { status, progress, invoice_id }     │           │
│  │ ├─ POST /api/invoices/list                         │           │
│  │ │  └─ Fetch saved invoices for chat context       │           │
│  │ └─ Health check + Swagger docs (/docs)            │           │
│  └─────────────────────────────────────────────────────┘           │
│      ↓ Jobs stored in DB                                           │
│  ┌─────────────────────────────────────────────────────┐           │
│  │ PostgreSQL Database                                 │           │
│  │ ├─ ocr_jobs (id, filepath, status, invoice_id)    │           │
│  │ └─ invoices (id, code, type, buyer, total, conf) │           │
│  └─────────────────────────────────────────────────────┘           │
│      ↑ Background polling                                          │
│  ┌─────────────────────────────────────────────────────┐           │
│  │ OCR Worker (Python) - SEPARATE PROCESS             │           │
│  │ ├─ Poll ocr_jobs WHERE status='queued'            │           │
│  │ ├─ Run Tesseract OCR (real, no mock)              │           │
│  │ ├─ Extract fields via regex                       │           │
│  │ ├─ Save to invoices table                         │           │
│  │ └─ Update job status='done' + invoice_id          │           │
│  └─────────────────────────────────────────────────────┘           │
│                                                                     │
│  File Storage:                                                      │
│  └─ /uploads/ (local filesystem with UUID prefix)                 │
│                                                                     │
│  LLM Integration:                                                   │
│  └─ Groq (llama-3.3-70b) for chat with invoice context            │
│                                                                     │
│  Key Changes (v2.1):                                                │
│  └─ Flask removed ✅                                               │
│  └─ All endpoints on FastAPI:8000 ✅                              │
│  └─ No inter-process HTTP overhead ✅                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

```

---

## 📊 Request/Response Flow Diagram

```

SCENARIO: User uploads invoice image

┌──────────────────────────────────────────────────────────────────────┐
│ STEP 1: USER UPLOADS IMAGE │
├──────────────────────────────────────────────────────────────────────┤
│ │
│ User selects image: │
│ ┌─────────────────────┐ │
│ │ invoice.jpg │ │
│ │ 2.5 MB │ │
│ └─────────────────────┘ │
│ │ │
│ ↓ POST /upload-image │
│ ┌────────────────────────────────────────────────────┐ │
│ │ Frontend sends multipart/form-data │ │
│ │ - image: <binary> │ │
│ │ - user_id: "user123" │ │
│ └────────────────────────────────────────────────────┘ │
│ │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│ STEP 2: CHATBOT SAVES FILE & ENQUEUES JOB (50-100ms) │
├──────────────────────────────────────────────────────────────────────┤
│ │
│ 1. Save file: │
│ /uploads/abc123def456_invoice.jpg │
│ │
│ 2. Call /api/ocr/enqueue: │
│ { │
│ "filepath": "/uploads/abc123def456_invoice.jpg", │
│ "filename": "invoice.jpg", │
│ "uploader": "chatbot", │
│ "user_id": "user123" │
│ } │
│ │
│ 3. Backend creates job record: │
│ INSERT INTO ocr_jobs (id, filepath, status, ...) │
│ job_id = "550e8400-e29b-41d4-a716-446655440000" │
│ │
│ 4. Return immediately: │
│ { │
│ "success": true, │
│ "job_id": "550e8400-e29b-41d4-a716-446655440000", │
│ "status": "queued", │
│ "message": "File uploaded! Processing in background...", │
│ "timestamp": "2025-10-20T12:34:56.789Z" │
│ } │
│ │
│ ✅ USER SEES RESPONSE IN ~50ms (no waiting for OCR!) │
│ │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│ STEP 3: WORKER PROCESSES JOB (BACKGROUND - INDEPENDENT) │
├──────────────────────────────────────────────────────────────────────┤
│ │
│ Poll loop (every 5 seconds): │
│ │
│ 1. SELECT \* FROM ocr_jobs WHERE status='queued' LIMIT 3 │
│ → Found job 550e8400-... │
│ │
│ 2. UPDATE ocr_jobs SET status='processing' WHERE id=... │
│ → Prevent duplicate processing │
│ │
│ 3. Load image from /uploads/abc123def456_invoice.jpg │
│ ↓ │
│ 4. Run Tesseract OCR: │
│ pytesseract.image_to_string(image, lang='vie+eng') │
│ → "HÓA ĐƠN\nMã: INV-2025-001\nNgày: 20/10/2025\n..." │
│ ↓ │
│ 5. Extract fields (regex patterns): │
│ { │
│ "invoice_code": "INV-2025-001", │
│ "date": "20/10/2025", │
│ "buyer_name": "CÔNG TY ABC", │
│ "seller_name": "CÔNG TY XYZ", │
│ "total_amount": "5,000,000 VND", │
│ "invoice_type": "general" │
│ } │
│ ↓ │
│ 6. Calculate confidence score (0.0-1.0): │
│ confidence = (ocr_quality + pattern_match) / 2 = 0.94 │
│ ↓ │
│ 7. Save to invoices table: │
│ INSERT INTO invoices (...) VALUES (...) │
│ → invoice_id = 42 │
│ ↓ │
│ 8. Update job status: │
│ UPDATE ocr_jobs │
│ SET status='done', invoice_id=42, completed_at=now() │
│ WHERE id='550e8400-...' │
│ │
│ ✅ JOB COMPLETE (2-5 seconds after enqueue) │
│ │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│ STEP 4: FRONTEND POLLS JOB STATUS (OPTIONAL) │
├──────────────────────────────────────────────────────────────────────┤
│ │
│ Frontend requests: │
│ GET /api/ocr/job/550e8400-e29b-41d4-a716-446655440000 │
│ │
│ Response: │
│ { │
│ "job_id": "550e8400-e29b-41d4-a716-446655440000", │
│ "filename": "invoice.jpg", │
│ "status": "done", │
│ "progress": 100, │
│ "invoice_id": 42, │
│ "error_message": null, │
│ "created_at": "2025-10-20T12:34:56.789Z", │
│ "updated_at": "2025-10-20T12:35:02.123Z" │
│ } │
│ │
│ Frontend: "✅ Processing complete! Invoice ID: 42" │
│ │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│ STEP 5: USER VIEWS/CHATS ABOUT INVOICE │
├──────────────────────────────────────────────────────────────────────┤
│ │
│ User: "Hóa đơn vừa upload có những gì?" │
│ │
│ Smart Chat Handler: │
│ 1. Query DB: SELECT \* FROM invoices WHERE id=42 │
│ 2. Build system prompt with real invoice data: │
│ "Expert về hóa đơn VN. Real data: │
│ - Invoice INV-2025-001, general type, buyer CÔNG TY ABC │
│ - Date 20/10/2025, total 5M VND, confidence 94%" │
│ 3. Send to Groq LLM │
│ 4. Return intelligent response: │
│ "Hóa đơn INV-2025-001 là loại hóa đơn chung. │
│ Số tiền: 5,000,000 VND. Khách: CÔNG TY ABC. │
│ Độ tin cậy: 94%. Đây là hóa đơn đầy đủ và hợp lệ." │
│ │
│ ✅ INTELLIGENT RESPONSE WITH REAL DATA │
│ │
└──────────────────────────────────────────────────────────────────────┘

```

---

## 🔄 Data Flow: Upload → Job → Invoice

```

                        ┌─────────────────────┐
                        │   FRONTEND (React)  │
                        └──────────┬──────────┘
                                   │ upload image
                                   ↓
                    ┌──────────────────────────────┐
                    │  CHATBOT (/upload-image)     │
                    │  (Flask :5001)               │
                    ├──────────────────────────────┤
                    │ • Save to /uploads/          │
                    │ • Call /api/ocr/enqueue      │
                    │ • Return job_id immediately  │
                    └──────────┬───────────────────┘
                               │ job_id returned (50-100ms)
                               ↓
                    ┌──────────────────────────────┐
                    │  FRONTEND shows progress     │
                    │  "Processing..."             │
                    └──────────┬───────────────────┘
                               │ (optionally polls status)
                               ↓
                    ┌──────────────────────────────┐
                    │  BACKEND API (/api/ocr/...)  │
                    │  (FastAPI :8000)             │
                    ├──────────────────────────────┤
                    │ • /api/ocr/enqueue           │
                    │   - Create ocr_jobs record   │
                    │   - Return job_id            │
                    │ • /api/ocr/job/{job_id}      │
                    │   - Check job status         │
                    │   - Return progress          │
                    └──────────┬───────────────────┘
                               │ stores jobs in DB
                               ↓
                    ┌──────────────────────────────┐
                    │  PostgreSQL                  │
                    ├──────────────────────────────┤
                    │ ocr_jobs table:              │
                    │ • id (UUID)                  │
                    │ • filepath                   │
                    │ • status (queued → done)     │
                    │ • invoice_id (after done)    │
                    │                              │
                    │ invoices table:              │
                    │ • id, code, type, buyer      │
                    │ • seller, amount, confidence │
                    └──────────┬───────────────────┘
                               ↑ (polls and updates)
                    ┌──────────────────────────────┐
                    │  WORKER (Separate Process)   │
                    │  (Python :background)        │
                    ├──────────────────────────────┤
                    │ 1. Poll ocr_jobs (every 5s)  │
                    │ 2. Load image from /uploads/ │
                    │ 3. Run Tesseract OCR         │
                    │ 4. Extract fields (regex)    │
                    │ 5. Calculate confidence      │
                    │ 6. Save invoice to DB        │
                    │ 7. Update job status='done'  │
                    │ 8. (Future) Emit WebSocket   │
                    └──────────┬───────────────────┘
                               │ invoice_id returned
                               ↓
                    ┌──────────────────────────────┐
                    │  FRONTEND/CHAT updates       │
                    │  Displays saved invoice      │
                    └──────────────────────────────┘

```

---

## 📋 API Contracts

### 1. Upload Image (Chatbot)

```

POST /upload-image (chatbot:5001)

Request:
Content-Type: multipart/form-data

- image: <binary file>
- user_id: string (optional)

Response (200 OK):
{
"success": true,
"message": "📋 File uploaded! Processing in background (Job ID: ...)",
"type": "job_enqueued",
"job_id": "550e8400-e29b-41d4-a716-446655440000",
"filename": "invoice.jpg",
"status": "queued",
"suggestions": ["Xem trạng thái job", "Danh sách hóa đơn"],
"timestamp": "2025-10-20T12:34:56.789Z"
}

Time: ~50-100ms (file saved, enqueued, returns immediately)

```

### 2. Enqueue OCR Job (Backend)

```

POST /api/ocr/enqueue (backend:8000)

Request:
{
"filepath": "/uploads/abc123_invoice.jpg",
"filename": "invoice.jpg",
"uploader": "chatbot",
"user_id": "user123"
}

Response (200 OK):
{
"success": true,
"job_id": "550e8400-e29b-41d4-a716-446655440000",
"status": "queued",
"message": "OCR job 550e8400-... queued successfully",
"filename": "invoice.jpg",
"timestamp": "2025-10-20T12:34:56.789Z"
}

Time: ~10-20ms (creates DB record)

```

### 3. Check Job Status (Backend)

```

GET /api/ocr/job/{job_id} (backend:8000)

Response (200 OK) - While Processing:
{
"success": true,
"job_id": "550e8400-e29b-41d4-a716-446655440000",
"filename": "invoice.jpg",
"status": "processing",
"progress": 45,
"invoice_id": null,
"error_message": null,
"created_at": "2025-10-20T12:34:56Z",
"updated_at": "2025-10-20T12:34:58Z"
}

Response (200 OK) - When Done:
{
"success": true,
"job_id": "550e8400-e29b-41d4-a716-446655440000",
"filename": "invoice.jpg",
"status": "done",
"progress": 100,
"invoice_id": 42,
"error_message": null,
"created_at": "2025-10-20T12:34:56Z",
"updated_at": "2025-10-20T12:35:02Z"
}

Response (200 OK) - If Failed:
{
"success": true,
"job_id": "550e8400-e29b-41d4-a716-446655440000",
"filename": "invoice.jpg",
"status": "failed",
"progress": 0,
"invoice_id": null,
"error_message": "Tesseract OCR failed or is not installed",
"created_at": "2025-10-20T12:34:56Z",
"updated_at": "2025-10-20T12:35:02Z"
}

```

---

## 🗂️ File Structure

```

f:\DoAnCN\
├── backend/
│ ├── main.py ← FastAPI app + /api/ocr/enqueue, /api/ocr/job/{job_id}
│ ├── worker.py ← OCR worker (separate process, polls & processes jobs)
│ ├── sql/
│ │ └── create_ocr_jobs.sql ← Migration: creates ocr_jobs table
│ └── requirements.txt ← Updated with pytesseract, Pillow
│
├── chatbot/
│ ├── app.py ← /upload-image now enqueues jobs
│ ├── handlers/
│ │ ├── chat_handler.py ← Pattern-based handler
│ │ ├── hybrid_chat_handler.py ← Groq LLM integration
│ │ └── smart_chat_handler.py ← Real invoice data → Groq context
│ └── requirements.txt
│
├── uploads/ ← NEW: stores uploaded images
│ └── (uploaded files saved here)
│
├── ARCHITECTURE_DIAGRAM.md ← This file (visual architecture)
└── ASYNC_OCR_SETUP.md ← Setup & troubleshooting guide

```

---

## 🚀 Deployment Timeline

```

T+0:00 User uploads image
↓
T+0.05s File saved, enqueue called
↓
T+0.10s Frontend gets job_id, shows "Processing..."
↓
T+5.00s Worker polls DB, finds job
↓
T+5.10s Worker runs Tesseract OCR (2-5s)
↓
T+5.70s Worker extracts fields, calculates confidence
↓
T+5.80s Worker inserts into invoices table
↓
T+5.90s Worker updates job_status='done', invoice_id=42
↓
T+6.00s Frontend polls /api/ocr/job/{id} → status='done'
↓
T+6.10s Frontend shows "✅ Done! Invoice ID: 42"
↓
T+6.20s User can chat about invoice using Groq LLM

```

---

## 💡 Key Advantages

✅ **No Mock Data**

- Worker uses real Tesseract OCR (not fallback generator)
- If OCR fails, job marked as 'failed' (not saved to DB)

✅ **Fast Upload Response**

- Upload returns in 50-100ms (not waiting for OCR)
- User immediately sees job_id and progress

✅ **Reliable Background Processing**

- Worker runs separately, independent of HTTP requests
- No timeouts, no connection drops affecting OCR

✅ **Transparent Status**

- Frontend can poll job status at any time
- Can see progress: queued → processing → done/failed

✅ **Real Data in Chat**

- Smart Chat Handler queries real invoices from DB
- Groq LLM receives actual extracted data in context

✅ **Scalable**

- Can run multiple workers in parallel
- Job table provides natural queue/deduplication
- Future: migrate to Redis/Celery for even better scale

---

## ⚙️ Configuration

**Worker Environment Variables:**

```

POLL_INTERVAL=5 # seconds between polls
MAX_JOBS_PER_POLL=3 # max jobs per poll cycle
TESSERACT_PATH=/usr/... # optional, auto-detect on PATH

```

**Database:**

- PostgreSQL with `ocr_jobs` and `invoices` tables
- Indexes on `ocr_jobs(status, created_at)` for fast polling

**Storage:**

- Local filesystem: `/uploads/` folder
- Future: AWS S3, Azure Blob Storage

---

## 🔗 Component Communication

```

Frontend (React)
↔ (REST API)
Chatbot (Flask:5001)
↔ (REST API)
Backend (FastAPI:8000)
↔ (SQL)
PostgreSQL
↑
Worker (Polling)
↑
File System (/uploads/)

```

---

## 📞 Support & Next Steps

See `ASYNC_OCR_SETUP.md` for:

- How to start each service (Backend, Chatbot, Worker)
- API usage examples with curl
- Troubleshooting guide
- Performance tuning

```

```

```
