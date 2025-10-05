# 🔄 Azure Storage + RAG Workflow

## 📋 Overview

Hệ thống sử dụng **Azure Storage** + **RAG (Retrieval-Augmented Generation)** để lưu trữ và query documents thay vì PostgreSQL.

## 🎯 Kiến trúc

```
┌─────────────┐
│   User      │
│  Upload     │
│   Image     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  Backend: /chat/upload-image/{session}  │
└──────┬──────────────────────────────────┘
       │
       ├─► 1️⃣ OCR Service (Tesseract + OpenCV)
       │   ├─ Extract text
       │   ├─ Parse invoice structure
       │   └─ Return: invoice_code, buyer, amount, etc.
       │
       ├─► 2️⃣ Azure Storage
       │   ├─ Upload image → blob storage
       │   ├─ Get permanent URL
       │   └─ Save to DocumentStorage table
       │
       ├─► 3️⃣ RAG Vector Database
       │   ├─ Embed OCR text with sentence-transformers
       │   ├─ Store vectors in ChromaDB
       │   └─ Enable semantic search
       │
       └─► 4️⃣ WebSocket Notification
           ├─ Send real-time OCR results to chat
           ├─ Show: filename, invoice_code, buyer, amount
           └─ Suggest: "xem số hóa đơn", "tìm kiếm"
```

## 🔍 Query Flow

```
┌──────────────┐
│    User      │
│  "xem số     │
│  hóa đơn"    │
└──────┬───────┘
       │
       ▼
┌─────────────────────────┐
│  Chatbot (Flask)        │
│  Pattern matching       │
│  → Intent: data_query   │
└──────┬──────────────────┘
       │
       ▼
┌────────────────────────────────┐
│  POST /chat/rag-search         │
│  {                             │
│    "query": "xem số hóa đơn",  │
│    "top_k": 5                  │
│  }                             │
└──────┬─────────────────────────┘
       │
       ▼
┌─────────────────────────┐
│  RAG Service            │
│  ├─ Embed query         │
│  ├─ Search vectors      │
│  └─ Return top 5 docs   │
└──────┬──────────────────┘
       │
       ▼
┌──────────────────────────┐
│  Response to Chatbot     │
│  {                       │
│    "results": [          │
│      {                   │
│        "content": "...", │
│        "score": 0.95,    │
│        "metadata": {...} │
│      }                   │
│    ]                     │
│  }                       │
└──────┬───────────────────┘
       │
       ▼
┌─────────────────────────┐
│  Chatbot Format         │
│  + Google AI Analysis   │
│  → Display to User      │
└─────────────────────────┘
```

## 📂 File Structure

### Backend Files

```
fastapi_backend/
├── routes/
│   └── websocket_chat.py       # ✅ Upload + RAG search endpoints
├── services/
│   ├── azure_service.py        # ☁️ Azure blob storage
│   ├── rag_service.py          # 🔍 Vector DB + semantic search
│   └── ocr_service.py          # 📄 OCR processing (NO PostgreSQL)
└── models/
    └── chat_models.py          # 💾 DocumentStorage model
```

### Chatbot Files

```
chatbot/
├── handlers/
│   └── chat_handler.py         # 🤖 Pattern matching + RAG query
└── utils/
    └── (database_tools.py)     # ❌ DELETED - not used
```

## 🔧 Key Endpoints

### 1. Upload Image

```http
POST /chat/upload-image/{session_id}
Content-Type: multipart/form-data

file: <image_file>
```

**Response:**

```json
{
  "success": true,
  "ocr_result": {
    "filename": "mau-hoa-don-mtt.jpg",
    "invoice_code": "MTT-001",
    "buyer_name": "CÔNG TY ABC",
    "total_amount": "1,500,000 VND"
  },
  "azure_url": "https://...",
  "rag_processed": true
}
```

**WebSocket Notification:**

```json
{
  "type": "ocr_completed",
  "message": "✅ Đã xử lý hoàn tất!\n📄 File: ...\n☁️ Azure: ✅\n🔍 RAG: ✅",
  "invoice_code": "MTT-001",
  "buyer_name": "CÔNG TY ABC"
}
```

### 2. RAG Semantic Search

```http
POST /chat/rag-search
Content-Type: application/json

{
  "query": "xem số hóa đơn",
  "top_k": 5
}
```

**Response:**

```json
{
  "success": true,
  "query": "xem số hóa đơn",
  "results_count": 3,
  "results": [
    {
      "content": "Invoice: MTT-001\nBuyer: CÔNG TY ABC\nAmount: 1,500,000 VND",
      "score": 0.95,
      "metadata": {
        "source": "chat_upload",
        "invoice_code": "MTT-001"
      }
    }
  ]
}
```

### 3. System Stats

```http
GET /chat/stats
```

**Response:**

```json
{
  "total_sessions": 10,
  "total_messages": 150,
  "total_documents": 25,
  "total_queries": 50,
  "active_connections": 3,
  "rag_stats": {
    "total_documents": 25,
    "total_vectors": 5000
  }
}
```

## 🎨 Pattern Matching

Chatbot `data_query` intent patterns:

```python
'data_query': [
    r'(xem dữ liệu|dữ liệu hiện tại|data)',
    r'(thống kê|báo cáo|report)',
    r'(có bao nhiêu|bao nhiêu|tổng số|đếm|count|số lượng)',
    r'(xem số|xem tổng|xem toàn bộ)',
    r'(hóa đơn|hoá đơn|invoice)',
]
```

**Example queries:**

- ✅ "xem số hóa đơn" → RAG search
- ✅ "có bao nhiêu hóa đơn" → RAG search
- ✅ "tìm hóa đơn CÔNG TY ABC" → RAG search
- ✅ "thống kê" → System stats

## 💾 Data Storage

### Azure Storage (Blob)

- **Purpose:** Permanent image storage
- **Access:** Public URL
- **Format:** Original images (jpg, png, pdf)

### RAG Vector Database (ChromaDB)

- **Purpose:** Semantic search
- **Content:** OCR extracted text + metadata
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2)

### SQLite (DocumentStorage)

- **Purpose:** Metadata + relationship tracking
- **Fields:** file_name, azure_url, ocr_results, extracted_data

## 🚀 Workflow Example

### Upload Flow:

```
1. User uploads "mau-hoa-don-mtt.jpg"
   ↓
2. OCR extracts:
   - invoice_code: "MTT-001"
   - buyer_name: "CÔNG TY ABC"
   - total_amount: "1,500,000 VND"
   ↓
3. Azure Storage saves image → URL
   ↓
4. RAG embeds text:
   "Invoice MTT-001, Buyer CÔNG TY ABC, Amount 1,500,000 VND"
   ↓
5. WebSocket sends notification to chat:
   "✅ Đã xử lý! Mã HĐ: MTT-001, Khách: CÔNG TY ABC"
```

### Query Flow:

```
1. User asks "xem số hóa đơn"
   ↓
2. Chatbot detects intent: data_query
   ↓
3. POST /chat/rag-search {"query": "xem số hóa đơn"}
   ↓
4. RAG searches similar documents
   ↓
5. Returns top 5 matching invoices with scores
   ↓
6. Chatbot formats:
   "🔍 Tìm thấy 3 hóa đơn:
    1. MTT-001 - CÔNG TY ABC (Score: 0.95)
    2. MTT-002 - CÔNG TY XYZ (Score: 0.87)"
   ↓
7. Google AI adds analysis
```

## ⚡ Performance

- **OCR:** ~2-5s per image
- **Azure Upload:** ~1-2s
- **RAG Indexing:** ~0.5s per document
- **RAG Search:** ~0.2-0.5s (top 5)
- **Total Upload:** ~4-8s end-to-end

## 🔐 Configuration

### Environment Variables

```env
# Azure Storage
AZURE_STORAGE_CONNECTION_STRING=...
AZURE_CONTAINER_NAME=invoice-images

# Google AI (for enhanced responses)
GOOGLE_AI_API_KEY=AIzaSy...

# RAG (optional - has fallback)
CHROMA_PERSIST_DIRECTORY=./chroma_db
```

### Dependencies

```txt
# Azure
azure-storage-blob

# RAG (optional)
sentence-transformers
chromadb

# OCR
pytesseract
opencv-python
Pillow
```

## 🎯 Benefits

### ✅ Advantages vs PostgreSQL:

1. **Semantic Search:** RAG finds similar invoices by meaning, not just keywords
2. **Scalability:** Azure handles large files + traffic
3. **No Schema:** Flexible document structure
4. **Cloud-Native:** Works anywhere, no local DB
5. **AI-Ready:** Embeddings enable advanced features

### ⚠️ Tradeoffs:

1. Requires sentence-transformers (large model ~90MB)
2. Slightly slower than SQL for exact matches
3. Vector DB maintenance needed

## 📝 Future Enhancements

- [ ] Multi-language support (EN, VI, etc.)
- [ ] PDF OCR with layout preservation
- [ ] Batch upload processing
- [ ] Advanced filters (date range, amount range)
- [ ] Export to Excel/CSV
- [ ] Invoice validation rules
- [ ] Duplicate detection

## 🐛 Troubleshooting

### RAG not available

```
⚠️ RAG dependencies not available: No module named 'sentence_transformers'
```

**Fix:** `pip install sentence-transformers chromadb`

### Azure upload failed

```
❌ Azure/RAG processing failed (non-critical)
```

**Check:** AZURE_STORAGE_CONNECTION_STRING in .env

### No search results

```
📊 Hệ thống có 0 tài liệu
```

**Fix:** Upload at least one invoice first

---

**Last Updated:** 2025-10-01
**Version:** 2.0 (Azure + RAG)
