# 🎉 POSTGRESQL FILE STORAGE - SETUP HOÀN TẤT!

## ✅ **ĐÃ TRIỂN KHAI XONG!**

Hệ thống giờ **LƯU FILE TRỰC TIẾP VÀO POSTGRESQL** - Không cần cloud, không cần API, hoàn toàn miễn phí!

---

## 📊 **KIẾN TRÚC MỚI:**

```
User Upload File
    ↓
Backend receives file bytes
    ↓
PostgreSQL Database
    ├─ file_content (BYTEA) → File binary
    ├─ content_type         → image/png
    ├─ file_size            → 163KB
    ├─ file_name            → invoice.png
    └─ ocr_results (JSON)   → Structured data
    ↓
✅ SAVED - NO CLOUD, NO API, NO COST!
```

---

## 🚀 **3 API endpoints MỚI:**

### **1. List Files (Danh sách)**

```bash
GET /chat/list-files-postgres?session_id={optional}&limit={optional}

# Example:
curl http://localhost:8000/chat/list-files-postgres?limit=10

# Response:
{
  "success": true,
  "count": 10,
  "storage": "PostgreSQL (Local - NO CLOUD)",
  "files": [
    {
      "id": 1,
      "filename": "invoice.png",
      "content_type": "image/png",
      "size": 163176,
      "document_type": "invoice",
      "uploaded_at": "2025-10-03T20:44:49",
      "has_file_content": true,
      "download_url": "/chat/download-from-postgres/1",
      "preview_url": "/chat/preview-from-postgres/1"
    }
  ]
}
```

---

### **2. Download File (Tải xuống)**

```bash
GET /chat/download-from-postgres/{document_id}

# Example:
curl http://localhost:8000/chat/download-from-postgres/1 --output invoice.png

# Hoặc paste URL vào browser:
http://localhost:8000/chat/download-from-postgres/1
→ Tự động download file
```

**Frontend Usage:**

```javascript
// Download file
async function downloadFile(docId) {
  const url = `/chat/download-from-postgres/${docId}`;

  // Option 1: Open in new tab
  window.open(url, "_blank");

  // Option 2: Download with custom filename
  const link = document.createElement("a");
  link.href = url;
  link.download = "invoice.png";
  link.click();
}
```

---

### **3. Preview File (Xem trước base64)**

```bash
GET /chat/preview-from-postgres/{document_id}

# Example:
curl http://localhost:8000/chat/preview-from-postgres/1

# Response:
{
  "success": true,
  "document_id": 1,
  "filename": "invoice.png",
  "content_type": "image/png",
  "size": 163176,
  "content_base64": "iVBORw0KGgoAAAANSUhEUg...",
  "data_url": "data:image/png;base64,iVBORw0KGgo..."
}
```

**Frontend Usage:**

```javascript
// Preview image without download
async function previewFile(docId) {
  const res = await fetch(`/chat/preview-from-postgres/${docId}`);
  const data = await res.json();

  // Display in <img> tag
  document.getElementById("preview").src = data.data_url;

  // Or in modal
  const img = document.createElement("img");
  img.src = data.data_url;
  img.alt = data.filename;
  document.body.appendChild(img);
}
```

---

## 💾 **DATABASE SCHEMA:**

```sql
-- DocumentStorage table
CREATE TABLE document_storage (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255),
    file_path TEXT,

    -- ⭐ FILE STORAGE (Binary)
    file_content BYTEA,          -- File bytes
    content_type VARCHAR(50),    -- MIME type
    file_size INTEGER,           -- Size in bytes

    -- Metadata
    azure_url TEXT,              -- Optional (null if not using Azure)
    ocr_results JSON,            -- OCR output
    extracted_data JSON,         -- Structured data
    document_type VARCHAR(50),   -- invoice, receipt, etc.
    upload_session VARCHAR(100), -- Session ID
    created_at TIMESTAMP DEFAULT NOW()
);

-- Example data:
-- id: 1
-- file_name: "invoice.png"
-- file_content: \x89504e470d0a1a0a... (binary)
-- content_type: "image/png"
-- file_size: 163176
-- ocr_results: {...JSON data...}
```

---

## 🧪 **TESTING:**

### **Test 1: Upload file**

```bash
# Upload qua UI hoặc curl
curl -X POST http://localhost:8000/chat/upload \
  -F "file=@test_invoice.png"

# Check backend log:
# ✅ Saved to PostgreSQL: ID=1, Size=163176 bytes - NO CLOUD, NO API!
```

### **Test 2: Verify in database**

```bash
# Connect to PostgreSQL
psql -U postgres -d chatbotdb

# Check file saved
SELECT id, file_name, file_size, content_type, created_at
FROM document_storage
ORDER BY id DESC
LIMIT 5;

# Check file content exists
SELECT id, file_name,
       LENGTH(file_content) as size_bytes,
       pg_size_pretty(LENGTH(file_content)::bigint) as size_readable
FROM document_storage;

# Output:
#  id |   file_name   | size_bytes | size_readable
# ----+---------------+------------+---------------
#   1 | invoice.png   |     163176 | 159 kB
```

### **Test 3: List files via API**

```bash
curl http://localhost:8000/chat/list-files-postgres

# Should return:
# {
#   "success": true,
#   "count": 1,
#   "storage": "PostgreSQL (Local - NO CLOUD)",
#   "files": [...]
# }
```

### **Test 4: Download file**

```bash
# Download file
curl http://localhost:8000/chat/download-from-postgres/1 \
  --output downloaded_invoice.png

# Verify file
file downloaded_invoice.png
# Output: PNG image data, 1024 x 768, 8-bit/color RGB, non-interlaced

# Compare with original
diff test_invoice.png downloaded_invoice.png
# Output: (no output = identical files)
```

### **Test 5: Preview base64**

```bash
curl http://localhost:8000/chat/preview-from-postgres/1 | jq .data_url

# Copy data_url và paste vào browser address bar
# → Should display image
```

---

## 📊 **STORAGE SIZE CALCULATOR:**

```python
# Ước tính storage cần thiết:

# Mỗi invoice ảnh PNG (average):
1 invoice = 200KB (average)

# 100 invoices:
100 × 200KB = 20MB

# 1000 invoices:
1000 × 200KB = 200MB

# 10,000 invoices:
10,000 × 200KB = 2GB

# PostgreSQL max database size:
# - Default: Unlimited (limited by disk space)
# - Recommended: < 10GB cho performance tốt
# - Max row size: 1GB
# - Max BYTEA column: 1GB
```

**Khuyến nghị:**

- ✅ < 1000 invoices: PostgreSQL perfect
- ⚠️ 1000-5000 invoices: PostgreSQL OK, consider optimization
- ❌ > 5000 invoices: Consider cloud storage (Supabase, Cloudinary)

---

## 🔧 **MAINTENANCE:**

### **Check database size:**

```sql
-- Total database size
SELECT pg_size_pretty(pg_database_size('chatbotdb')) as db_size;

-- Table size
SELECT
    pg_size_pretty(pg_total_relation_size('document_storage')) as total_size,
    pg_size_pretty(pg_relation_size('document_storage')) as table_size,
    pg_size_pretty(pg_total_relation_size('document_storage') - pg_relation_size('document_storage')) as index_size;

-- Average file size
SELECT
    COUNT(*) as total_files,
    pg_size_pretty(AVG(file_size)::bigint) as avg_file_size,
    pg_size_pretty(SUM(file_size)::bigint) as total_storage
FROM document_storage
WHERE file_content IS NOT NULL;
```

### **Cleanup old files:**

```sql
-- Delete files older than 30 days
DELETE FROM document_storage
WHERE created_at < NOW() - INTERVAL '30 days';

-- Or soft delete (add is_deleted column)
UPDATE document_storage
SET file_content = NULL  -- Remove binary data, keep metadata
WHERE created_at < NOW() - INTERVAL '30 days';
```

### **Optimize database:**

```sql
-- Vacuum (reclaim space)
VACUUM FULL document_storage;

-- Analyze (update statistics)
ANALYZE document_storage;

-- Reindex
REINDEX TABLE document_storage;
```

---

## 🆚 **SO SÁNH: PostgreSQL vs Cloud Storage**

| Feature           | PostgreSQL Local    | Azure/Cloud                 |
| ----------------- | ------------------- | --------------------------- |
| **Setup**         | ✅ Đã có sẵn        | ❌ Cần account, credit card |
| **Chi phí**       | ✅ $0               | ❌ $2-10/month              |
| **Internet**      | ✅ Không cần        | ❌ Cần internet             |
| **API calls**     | ✅ Không cần        | ❌ Cần REST API             |
| **Speed (Local)** | ⚡ Cực nhanh        | 🐢 Phụ thuộc network        |
| **Backup**        | ⚠️ Manual (pg_dump) | ✅ Auto backup              |
| **Scalability**   | ⚠️ Limited by disk  | ✅ Unlimited                |
| **Multi-server**  | ❌ Không share được | ✅ Share được               |
| **Security**      | ✅ Local = bảo mật  | ⚠️ Phụ thuộc config         |

---

## ✅ **ĐÃ THAY ĐỔI:**

### **1. Model (chat_models.py):**

```python
# ✅ ĐÃ CÓ các columns:
- file_content: LargeBinary  # Binary file data
- content_type: String       # MIME type
- file_size: Integer         # Size in bytes
```

### **2. Upload Logic (websocket_chat.py):**

```python
# ✅ ĐÃ LƯU file content vào database:
document = DocumentStorage(
    file_content=file_content,  # Binary bytes
    content_type="image/png",
    file_size=len(file_content)
)
```

### **3. Azure Upload:**

```python
# ⚠️ ĐÃ DISABLE (commented out)
# Có thể enable lại nếu cần:
# - Uncomment Azure upload code
# - Add AZURE_STORAGE_CONNECTION_STRING vào .env
```

### **4. APIs Added:**

```python
# ✅ 3 endpoints mới:
- GET /chat/list-files-postgres        # List files
- GET /chat/download-from-postgres/{id} # Download
- GET /chat/preview-from-postgres/{id}  # Preview base64
```

---

## 🚀 **NEXT STEPS:**

### **Option 1: Dùng PostgreSQL local (Hiện tại)**

```bash
✅ Không làm gì cả - Đã xong!
✅ Upload file → Tự động lưu vào PostgreSQL
✅ Download/Preview qua APIs
✅ Hoàn toàn miễn phí, không cần internet
```

### **Option 2: Upgrade lên Cloud sau (Khi cần)**

```bash
# Khi nào cần?
- Có > 5000 invoices (database quá lớn)
- Deploy lên cloud server (Heroku, Railway)
- Cần multi-server access
- Cần auto backup

# Chọn cloud:
- Supabase: Free 1GB + PostgreSQL integrated
- Cloudinary: Free 25GB + auto image optimization
- Azure: Paid, enterprise-grade
```

---

## 📝 **SUMMARY:**

**✅ Đã implement:**

- Lưu file vào PostgreSQL (BYTEA column)
- 3 APIs: list, download, preview
- Disable Azure upload (commented out)
- Full documentation

**✅ Hiện tại:**

- Upload file → PostgreSQL local
- Không cần cloud, không cần API
- Hoàn toàn miễn phí ($0)
- Tốc độ cực nhanh (local database)

**✅ Bạn có thể:**

- Upload invoices qua UI
- List tất cả files: `/chat/list-files-postgres`
- Download: `/chat/download-from-postgres/{id}`
- Preview: `/chat/preview-from-postgres/{id}`

**🎉 HỆ THỐNG SẴN SÀNG!** 🚀
