# 🎯 PostgreSQL File Storage - KHÔNG CẦN API, KHÔNG CẦN CLOUD!

## ✅ **ĐÃ IMPLEMENT: Lưu file trực tiếp vào PostgreSQL**

---

## 🚀 **CÁCH HOẠT ĐỘNG:**

### **Trước (Cần Azure):**

```
User upload invoice.png
    ↓
Backend receives file
    ↓
Call Azure API (cần internet)
    ↓
Upload to Azure Cloud (Singapore/US)
    ↓
Save metadata to PostgreSQL
```

### **Sau (PostgreSQL only):**

```
User upload invoice.png
    ↓
Backend receives file
    ↓
Save TRỰC TIẾP vào PostgreSQL (local)
    ↓
XONG! Không cần internet, không cần API!
```

---

## 📊 **SCHEMA MỚI:**

```sql
CREATE TABLE document_storage (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR,
    file_path VARCHAR,  -- Local path (optional)

    -- ⭐ LƯU FILE CONTENT
    file_content BYTEA,          -- Binary data
    content_type VARCHAR(50),    -- image/png, image/jpeg
    file_size INTEGER,           -- Size in bytes

    -- Azure (optional)
    azure_url VARCHAR,

    -- Metadata
    ocr_results JSON,
    extracted_data JSON,
    document_type VARCHAR,
    upload_session VARCHAR,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 💻 **CÁC API MỚI:**

### **1. Download File từ PostgreSQL**

```bash
GET /chat/download-from-postgres/{document_id}

# Example:
curl http://localhost:8000/chat/download-from-postgres/1 -o invoice.png

# Response: File binary (direct download)
```

**Frontend:**

```javascript
// Download file
async function downloadFromPostgres(docId) {
  const url = `/chat/download-from-postgres/${docId}`;
  window.open(url, "_blank"); // Direct download
}
```

---

### **2. Preview File (Base64)**

```bash
GET /chat/preview-from-postgres/{document_id}

# Response:
{
  "success": true,
  "data_url": "data:image/png;base64,iVBORw0KGgo...",
  "filename": "invoice.png",
  "size": 163176
}
```

**Frontend:**

```javascript
// Preview image
async function previewFromPostgres(docId) {
  const res = await fetch(`/chat/preview-from-postgres/${docId}`);
  const data = await res.json();

  // Display in <img>
  document.getElementById("preview").src = data.data_url;
}
```

---

### **3. List All Files**

```bash
GET /chat/list-files-postgres?limit=50

# Response:
{
  "success": true,
  "count": 10,
  "storage": "PostgreSQL (Local - NO CLOUD)",
  "files": [
    {
      "id": 1,
      "filename": "invoice.png",
      "size": 163176,
      "content_type": "image/png",
      "download_url": "/chat/download-from-postgres/1",
      "preview_url": "/chat/preview-from-postgres/1"
    }
  ]
}
```

**Frontend:**

```javascript
// List and display files
async function loadFiles() {
  const res = await fetch("/chat/list-files-postgres");
  const data = await res.json();

  data.files.forEach((file) => {
    console.log(`File: ${file.filename}, Size: ${file.size} bytes`);
    // Display thumbnail: <img src="/chat/preview-from-postgres/{file.id}" />
  });
}
```

---

## 🔧 **MIGRATION:**

### **Bước 1: Run SQL Migration**

```bash
# Connect to PostgreSQL
psql -U postgres -d chatbotdb

# Run migration
\i f:/DoAnCN/fastapi_backend/migrations/add_file_content_columns.sql

# Verify
SELECT column_name, data_type FROM information_schema.columns
WHERE table_name = 'document_storage';

# Should see:
# - file_content | bytea
# - content_type | character varying
# - file_size    | integer
```

### **Bước 2: Restart Backend**

```bash
cd f:\DoAnCN\fastapi_backend
python main.py

# Check log:
# INFO: Models updated with file_content support
```

### **Bước 3: Test Upload**

```bash
# Upload a file via UI or curl
curl -X POST http://localhost:8000/chat/upload \
  -F "file=@test_invoice.png"

# Check backend log:
# 💾 Saved to PostgreSQL: ID=11, Size=163176 bytes - NO CLOUD, NO API!
```

### **Bước 4: Test Download**

```bash
# Download file
curl http://localhost:8000/chat/download-from-postgres/11 -o downloaded.png

# Verify file
ls -lh downloaded.png
# Should be same size as original
```

---

## 📊 **SO SÁNH:**

| Feature           | Azure Storage            | PostgreSQL Storage     |
| ----------------- | ------------------------ | ---------------------- |
| **Setup**         | Cần account, credit card | Không cần gì cả        |
| **API Calls**     | Cần call API             | Không cần API          |
| **Internet**      | Bắt buộc                 | Không cần              |
| **Chi phí**       | $2-10/month              | $0                     |
| **Tốc độ**        | Fast (CDN global)        | Very fast (local)      |
| **Backup**        | Auto (GRS/LRS)           | Manual (pg_dump)       |
| **Max file size** | Unlimited                | 1GB/file (BYTEA limit) |
| **Scalability**   | Unlimited                | Giới hạn bởi disk      |
| **Security**      | SAS token                | Database permissions   |

---

## ✅ **ƯU ĐIỂM PostgreSQL Storage:**

### **1. Không cần Cloud Account**

- ✅ Không cần Azure account
- ✅ Không cần credit card
- ✅ Không cần verify email

### **2. Hoàn toàn Offline**

- ✅ Hoạt động không cần internet
- ✅ Không bị rate limit
- ✅ Không bị downtime của cloud

### **3. Chi phí $0**

- ✅ Miễn phí hoàn toàn
- ✅ Không lo billing
- ✅ Không surprise charges

### **4. Đơn giản**

- ✅ 1 database cho tất cả
- ✅ Backup cùng database
- ✅ Restore cùng database

### **5. ACID Transactions**

- ✅ Atomic: File + metadata cùng transaction
- ✅ Rollback được nếu error
- ✅ No orphaned files

---

## ⚠️ **GIỚI HẠN:**

### **1. File Size**

```
- Max 1GB/file (BYTEA limit)
- Recommend: < 10MB/file để performance tốt
- > 100MB → nên dùng cloud storage
```

### **2. Database Size**

```
- 1000 invoices x 500KB = 500MB
- 10,000 invoices x 500KB = 5GB
- 100,000 invoices → Cần optimize hoặc cloud
```

### **3. Performance**

```
- < 1GB database: Very fast
- 1-10GB: Good
- > 10GB: Consider archiving old data
```

### **4. Backup**

```
- Phải manual backup: pg_dump
- File size lớn → backup lâu hơn
```

---

## 🎯 **KHUYẾN NGHỊ:**

### **Dùng PostgreSQL Storage khi:**

- ✅ Development/testing
- ✅ File size nhỏ (< 10MB)
- ✅ Số lượng files ít (< 10,000)
- ✅ Không cần CDN
- ✅ Offline app
- ✅ Chi phí $0

### **Dùng Cloud Storage khi:**

- ⚠️ Production với nhiều users
- ⚠️ File size lớn (> 100MB)
- ⚠️ Số lượng files nhiều (> 100,000)
- ⚠️ Cần CDN global
- ⚠️ Multi-region backup
- ⚠️ Scalability unlimited

---

## 📝 **CODE EXAMPLES:**

### **Upload và lưu vào PostgreSQL:**

```python
# Trong websocket_chat.py (đã update)
file_content = await file.read()

document = DocumentStorage(
    file_name=file.filename,
    file_content=file_content,  # ⭐ Lưu binary
    content_type="image/png",
    file_size=len(file_content),
    ocr_results=json.dumps(ocr_result)
)
db.add(document)
db.commit()

# ✅ File đã lưu vào PostgreSQL!
# ✅ Không cần Azure, không cần API!
```

### **Download từ PostgreSQL:**

```python
# Trong API endpoint
doc = db.query(DocumentStorage).filter_by(id=1).first()

# Return file binary
return Response(
    content=doc.file_content,
    media_type=doc.content_type,
    headers={"Content-Disposition": f'attachment; filename="{doc.file_name}"'}
)
```

### **Preview base64:**

```python
import base64

doc = db.query(DocumentStorage).filter_by(id=1).first()
file_base64 = base64.b64encode(doc.file_content).decode('utf-8')

return {
    "data_url": f"data:{doc.content_type};base64,{file_base64}"
}

# Frontend: <img src={data_url} />
```

---

## 🧪 **TESTING:**

### **Test 1: Upload**

```bash
curl -X POST http://localhost:8000/chat/upload \
  -F "file=@invoice.png"

# Check log:
# 💾 Saved to PostgreSQL: ID=1, Size=163176 bytes - NO CLOUD, NO API!
```

### **Test 2: List Files**

```bash
curl http://localhost:8000/chat/list-files-postgres

# Response:
# {
#   "count": 1,
#   "storage": "PostgreSQL (Local - NO CLOUD)",
#   "files": [...]
# }
```

### **Test 3: Download**

```bash
curl http://localhost:8000/chat/download-from-postgres/1 -o test.png

# Verify
md5sum invoice.png test.png
# Should be identical
```

### **Test 4: Preview**

```bash
curl http://localhost:8000/chat/preview-from-postgres/1 | jq .data_url

# Copy data_url và paste vào browser address bar
# → Xem được ảnh!
```

---

## 📊 **DATABASE SIZE MONITORING:**

### **Check table size:**

```sql
SELECT
    pg_size_pretty(pg_total_relation_size('document_storage')) as total_size,
    pg_size_pretty(pg_relation_size('document_storage')) as table_size,
    pg_size_pretty(pg_indexes_size('document_storage')) as indexes_size;

-- Example output:
-- total_size | table_size | indexes_size
-- 2567 MB    | 2500 MB    | 67 MB
```

### **Check average file size:**

```sql
SELECT
    COUNT(*) as total_files,
    pg_size_pretty(AVG(octet_length(file_content))::bigint) as avg_file_size,
    pg_size_pretty(SUM(octet_length(file_content))::bigint) as total_file_size
FROM document_storage
WHERE file_content IS NOT NULL;
```

### **Find large files:**

```sql
SELECT
    id,
    file_name,
    pg_size_pretty(octet_length(file_content)::bigint) as file_size
FROM document_storage
WHERE file_content IS NOT NULL
ORDER BY octet_length(file_content) DESC
LIMIT 10;
```

---

## ✅ **SUMMARY:**

**✅ Đã implement thành công:**

- ✅ Model updated (file_content, content_type, file_size)
- ✅ Save logic updated (lưu file vào PostgreSQL)
- ✅ 3 APIs mới:
  - `/download-from-postgres/{id}`
  - `/preview-from-postgres/{id}`
  - `/list-files-postgres`
- ✅ Migration SQL script
- ✅ Documentation đầy đủ

**✅ Lợi ích:**

- ✅ Không cần Azure ($0 cost)
- ✅ Không cần API
- ✅ Không cần internet
- ✅ Hoàn toàn local
- ✅ ACID transactions
- ✅ Backup đơn giản (pg_dump)

**⚠️ Lưu ý:**

- Max 1GB/file (BYTEA limit)
- Recommend < 10MB/file
- Monitor database size
- Backup regularly

---

**🎉 Giờ bạn có hệ thống lưu trữ hoàn toàn KHÔNG CẦN CLOUD!**
