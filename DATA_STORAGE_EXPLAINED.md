# 💾 GIẢI THÍCH LUỒNG LƯU TRỮ DỮ LIỆU

## ❓ Câu Hỏi: "Khi tạo như vầy nó có lưu lại không?"

### ✅ TRẢ LỜI: **CÓ, HỆ THỐNG LƯU 3 NƠI!**

---

## 📊 Tổng Quan Luồng Lưu Trữ

```
User Upload Invoice
        ↓
┌───────────────────────────────────────┐
│   BƯỚC 1: OCR EXTRACTION              │
│   - Extract text với Tesseract/Azure  │
│   - Extract fields (số HĐ, tiền, v.v.) │
│   - Lưu file vào /uploads folder      │
└───────────────────────────────────────┘
        ↓
┌───────────────────────────────────────┐
│   BƯỚC 2: POSTGRESQL DATABASE         │
│   ✅ Lưu vào DocumentStorage table    │
│   - ID, filename, OCR results         │
│   - Azure URL, extracted data         │
│   - Timestamps                        │
└───────────────────────────────────────┘
        ↓
┌───────────────────────────────────────┐
│   BƯỚC 3: RAG VECTOR DATABASE         │
│   ✅ Lưu vào ChromaDB                 │
│   - Embeddings cho semantic search    │
│   - Full text content                 │
│   - Metadata                          │
└───────────────────────────────────────┘
        ↓
┌───────────────────────────────────────┐
│   OPTIONAL: AZURE BLOB STORAGE        │
│   ⚠️ Lưu image lên cloud (nếu có)     │
│   - Backup ảnh                        │
│   - Public URL                        │
└───────────────────────────────────────┘
```

---

## 💾 CHI TIẾT 3 NƠI LƯU TRỮ

### 1️⃣ **Local File System (`/uploads` folder)**

**Lưu gì:**

- ✅ File ảnh gốc
- ✅ Unique filename: `ocr_uuid.jpg`

**Đường dẫn:**

```
f:\DoAnCN\fastapi_backend\uploads\ocr_6a947157-66b4-4cf1-9aa8-97dbe31b7c5d.jpg
```

**Code:**

```python
# ocr_service.py - Line 88-98
async def store_file(self, file: UploadFile):
    file_ext = os.path.splitext(file.filename)[1].lower()
    unique_filename = f"ocr_{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(self.upload_dir, unique_filename)

    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)

    logger.info(f"✅ File stored: {file_path}")
```

**Persistent:** ✅ Yes (không bị mất khi restart)

---

### 2️⃣ **PostgreSQL Database (Bảng `DocumentStorage`)**

**Lưu gì:**

- ✅ Metadata của document
- ✅ OCR results (full JSON)
- ✅ Extracted data (invoice info)
- ✅ Azure URL (nếu có)
- ✅ Timestamps

**Table Structure:**

```sql
CREATE TABLE document_storage (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255),
    azure_url TEXT,
    ocr_results JSON,            -- Full OCR output
    extracted_data JSON,         -- Invoice fields
    document_type VARCHAR(50),
    upload_session VARCHAR(100),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

**Code:**

```python
# websocket_chat.py - Line 341-357
document = DocumentStorage(
    file_name=file.filename,
    azure_url=azure_url,  # Can be None
    ocr_results=json.dumps(ocr_result),  # Full JSON
    extracted_data=json.dumps({
        "invoice_code": ocr_result.get('invoice_code'),
        "buyer_name": ocr_result.get('buyer_name'),
        "total_amount": ocr_result.get('total_amount')
    }),
    document_type="invoice",
    upload_session=session_id
)
db.add(document)
db.commit()
db.refresh(document)
document_id = document.id
logger.info(f"💾 Saved to DocumentStorage: ID={document_id}")
```

**Ví dụ Data:**

```json
{
  "id": 7,
  "file_name": "mau-hoa-don-mtt.jpg",
  "azure_url": null,
  "ocr_results": {
    "invoice_code": "1C23MYY",
    "total_amount": "280.000",
    "buyer_name": "CPIIOANGLON",
    "raw_ocr_text": "Lap hoa don CONGTYCPIIOANGLON..."
  },
  "extracted_data": {
    "invoice_code": "1C23MYY",
    "buyer_name": "CPIIOANGLON",
    "total_amount": "280.000"
  },
  "document_type": "invoice",
  "upload_session": "54e8114596587c43",
  "created_at": "2025-10-03T10:30:00",
  "updated_at": "2025-10-03T10:30:00"
}
```

**Query Example:**

```sql
-- Xem tất cả documents
SELECT id, file_name, document_type, created_at
FROM document_storage
ORDER BY created_at DESC;

-- Xem chi tiết document ID 7
SELECT * FROM document_storage WHERE id = 7;

-- Đếm số lượng
SELECT COUNT(*) FROM document_storage;
```

**Persistent:** ✅ Yes (database permanent storage)

---

### 3️⃣ **ChromaDB Vector Database (RAG System)**

**Lưu gì:**

- ✅ Embeddings (vector 384 chiều)
- ✅ Full text content
- ✅ Metadata (invoice_code, filename, session)
- ✅ Chunks (split text thành đoạn)

**Location:**

```
f:\DoAnCN\fastapi_backend\chroma_db\
```

**Code:**

```python
# websocket_chat.py - Line 360-379
raw_text = ocr_result.get('raw_ocr_text', '')
structured_summary = f"""
Invoice: {ocr_result.get('invoice_code')}
Buyer: {ocr_result.get('buyer_name')}
Seller: {ocr_result.get('seller_name')}
Amount: {ocr_result.get('total_amount')}
Type: {ocr_result.get('invoice_type')}
"""
extracted_text = f"{structured_summary}\n\nFull OCR Text:\n{raw_text}"

rag_service.process_document_for_rag(
    document_id=document_id,
    content=extracted_text,
    metadata={
        "source": "chat_upload",
        "session": session_id,
        "invoice_code": ocr_result.get('invoice_code'),
        "filename": file.filename
    }
)
```

**RAG Processing:**

```python
# rag_service.py
def process_document_for_rag(self, document_id, content, metadata):
    # Split text into chunks
    chunks = self.text_splitter.split_text(content)

    # Generate embeddings
    embeddings = self.embedding_model.encode(chunks)

    # Store in ChromaDB
    self.collection.add(
        documents=chunks,
        embeddings=embeddings,
        metadatas=[metadata] * len(chunks),
        ids=[f"doc_{document_id}_chunk_{i}" for i in range(len(chunks))]
    )
```

**Data Structure:**

```json
{
  "id": "doc_7_chunk_0",
  "embedding": [0.123, -0.456, 0.789, ...],  // 384 dimensions
  "document": "Invoice: 1C23MYY\nBuyer: CPIIOANGLON...",
  "metadata": {
    "source": "chat_upload",
    "session": "54e8114596587c43",
    "invoice_code": "1C23MYY",
    "filename": "mau-hoa-don-mtt.jpg"
  }
}
```

**Persistent:** ✅ Yes (ChromaDB lưu vào disk)

---

### 4️⃣ **Azure Blob Storage (Optional, Cloud Backup)**

**Lưu gì:**

- ✅ File ảnh gốc
- ✅ Public URL để access

**Status:** ⚠️ **HIỆN TẠI KHÔNG HOẠT ĐỘNG** (chưa config)

**Code:**

```python
# websocket_chat.py - Line 325-338
try:
    upload_result = await azure_service.upload_image_to_azure(
        file_content=file_content,
        filename=file.filename,
        session_id=session_id
    )

    if upload_result["success"]:
        azure_url = upload_result["azure_url"]
        logger.info(f"☁️ Uploaded to Azure: {azure_url}")
except Exception as azure_error:
    logger.warning(f"⚠️ Azure upload failed (non-critical): {azure_error}")
```

**Khi Configured:**

```
Azure URL: https://doancn.blob.core.windows.net/chat-documents/54e8114/uuid.jpg
```

**Persistent:** ✅ Yes (cloud storage)

---

## 🔍 KIỂM TRA DỮ LIỆU ĐÃ LƯU

### Check 1: Local Files

```powershell
# Xem files đã upload
dir f:\DoAnCN\fastapi_backend\uploads\

# Kết quả:
# ocr_6a947157-66b4-4cf1-9aa8-97dbe31b7c5d.jpg
# ocr_4849a399-5ef6-46c8-ac61-4743b28feff9.png
```

### Check 2: PostgreSQL Database

```powershell
# Connect to database
psql -U postgres -d chatbotdb

# Query
SELECT id, file_name, document_type, created_at
FROM document_storage
ORDER BY id DESC
LIMIT 10;
```

**Kết quả:**

```
 id |        file_name        | document_type |       created_at
----+-------------------------+---------------+------------------------
  8 | hoa-don-ban-hang.png   | invoice       | 2025-10-03 10:35:22
  7 | mau-hoa-don-mtt.jpg    | invoice       | 2025-10-03 10:30:15
  6 | invoice-003.jpg         | invoice       | 2025-10-03 09:45:10
```

### Check 3: ChromaDB (RAG)

```python
# Test script
from services.rag_service import rag_service

# Get stats
stats = rag_service.get_stats()
print(f"Total documents: {stats['total_documents']}")
print(f"Total chunks: {stats['total_chunks']}")

# Search test
results = rag_service.search("hóa đơn 1C23MYY", top_k=3)
for i, result in enumerate(results):
    print(f"{i+1}. {result['metadata']['filename']}: {result['content'][:100]}")
```

**Output:**

```
Total documents: 3
Total chunks: 3

1. mau-hoa-don-mtt.jpg: Invoice: 1C23MYY
Buyer: CPIIOANGLON
Seller: CÔNG TY...

2. hoa-don-ban-hang.png: Invoice: OCR-202510031035
Buyer: Extracted from OCR...
```

### Check 4: Backend Logs

```powershell
# Check terminal logs
cd f:\DoAnCN\fastapi_backend
python main.py
```

**Log Output:**

```
INFO:routes.websocket_chat:📤 Chat upload: mau-hoa-don-mtt.jpg
INFO:ocr_service:✅ File stored: uploads\ocr_6a947157.jpg
INFO:routes.websocket_chat:✅ OCR completed
INFO:routes.websocket_chat:💾 Saved to DocumentStorage: ID=7
INFO:routes.websocket_chat:🔍 Processed for RAG: doc_id=7
```

---

## 📋 SUMMARY TABLE

| Storage Location                    | Data Type           | Persistent | Currently Working | Purpose         |
| ----------------------------------- | ------------------- | ---------- | ----------------- | --------------- |
| **Local Files** (`/uploads`)        | Original images     | ✅ Yes     | ✅ Yes            | File storage    |
| **PostgreSQL** (`document_storage`) | Metadata + OCR JSON | ✅ Yes     | ✅ Yes            | Structured data |
| **ChromaDB** (`chroma_db/`)         | Embeddings + text   | ✅ Yes     | ⚠️ Fallback mode  | Semantic search |
| **Azure Blob** (cloud)              | Image backup        | ✅ Yes     | ❌ Not configured | Cloud backup    |

---

## ✅ KẾT LUẬN

### Câu Trả Lời Chi Tiết:

**1. Có lưu không?**

- ✅ **CÓ!** Hệ thống lưu dữ liệu vào **3 nơi**:
  - Local files (`/uploads`)
  - PostgreSQL database (`document_storage` table)
  - ChromaDB vector database (RAG)

**2. Lưu ở đâu?**

- 📁 **File ảnh:** `f:\DoAnCN\fastapi_backend\uploads\`
- 🗄️ **Database:** PostgreSQL `chatbotdb` → table `document_storage`
- 🧠 **RAG:** `f:\DoAnCN\fastapi_backend\chroma_db\`

**3. Lưu cái gì?**

- 📷 **Ảnh gốc:** File image với unique ID
- 📊 **OCR results:** Full JSON với extracted text + fields
- 🔍 **Embeddings:** Vector cho semantic search
- 📋 **Metadata:** Invoice code, buyer, amount, v.v.

**4. Có mất khi restart không?**

- ✅ **KHÔNG MẤT!** Tất cả đều persistent:
  - Files lưu trên disk
  - PostgreSQL là database
  - ChromaDB lưu vào disk

**5. Có thể query lại không?**

- ✅ **CÓ!** 3 cách:
  - SQL query PostgreSQL
  - Semantic search qua RAG
  - Chatbot query: "xem hóa đơn đã lưu"

---

## 🧪 TEST NGAY

### Test Persistence:

1. **Upload invoice:**

   ```
   Frontend → Upload "test-invoice.jpg"
   ```

2. **Check database:**

   ```sql
   SELECT * FROM document_storage ORDER BY id DESC LIMIT 1;
   ```

3. **Restart backend:**

   ```powershell
   # Stop backend (Ctrl+C)
   # Start again
   python main.py
   ```

4. **Query lại:**
   ```
   Chatbot: "xem hóa đơn test-invoice"
   → Should find it! ✅
   ```

---

## 💡 Bonus: Backup & Restore

### Backup Database:

```bash
pg_dump -U postgres chatbotdb > backup_chatbotdb.sql
```

### Restore Database:

```bash
psql -U postgres chatbotdb < backup_chatbotdb.sql
```

### Backup Files:

```bash
xcopy /E /I uploads uploads_backup
```

**Tất cả dữ liệu đều ĐƯỢC LƯU và KHÔNG MẤT!** ✅
