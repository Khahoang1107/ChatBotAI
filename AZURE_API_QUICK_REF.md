# 📋 AZURE STORAGE API - QUICK REFERENCE

## ✅ **Câu hỏi: "Nếu lưu lên Azure Storage thì có thể gọi API tới để lấy dữ liệu không?"**

## ✅ **Trả lời: CÓ - Đã implement đầy đủ!**

---

## 🚀 **4 APIs CHÍNH:**

### **1. Download Invoice (Get secure URL)**

```bash
GET /chat/download-invoice/{document_id}

# Example:
curl http://localhost:8000/chat/download-invoice/9

# Response:
{
  "download_url": "https://storage.blob.core.windows.net/...?SAS_TOKEN",
  "expires_in": "1 hour"
}
```

### **2. List All Invoices**

```bash
GET /chat/list-invoices?session_id={optional}&limit={optional}

# Example:
curl http://localhost:8000/chat/list-invoices?limit=10

# Response:
{
  "count": 10,
  "invoices": [
    {"id": 9, "filename": "invoice.png", "download_url": "https://..."}
  ]
}
```

### **3. Get File Content (Base64)**

```bash
POST /chat/get-invoice-content/{document_id}

# Example:
curl -X POST http://localhost:8000/chat/get-invoice-content/9

# Response:
{
  "content_base64": "iVBORw0KGgo...",
  "data_url": "data:image/png;base64,..."
}
```

### **4. List Azure Blobs**

```bash
GET /chat/list-azure-blobs?session_id={optional}

# Example:
curl http://localhost:8000/chat/list-azure-blobs
```

---

## 💻 **Backend Methods (services/azure_service.py):**

```python
# 1. Generate secure URL
url = await azure_service.get_blob_download_url(
    blob_name="session_abc/invoice.png",
    expires_hours=1  # Auto-expire after 1 hour
)

# 2. Download file bytes
file_bytes = await azure_service.download_blob_content(
    blob_name="session_abc/invoice.png"
)

# 3. List all blobs
blobs = await azure_service.list_user_blobs(
    session_id="session_abc"  # Optional filter
)

# 4. Get blob properties
properties = await azure_service.get_blob_properties(
    blob_name="session_abc/invoice.png"
)

# 5. Delete blob
success = await azure_service.delete_blob(
    blob_name="session_abc/invoice.png"
)
```

---

## 🌐 **Frontend Usage:**

### **React/Vue/Angular:**

```javascript
// Download invoice
async function downloadInvoice(documentId) {
  const res = await fetch(`/chat/download-invoice/${documentId}`);
  const data = await res.json();

  // Open in new tab
  window.open(data.download_url, "_blank");

  // OR download as file
  const link = document.createElement("a");
  link.href = data.download_url;
  link.download = data.filename;
  link.click();
}

// List invoices
async function loadInvoices() {
  const res = await fetch("/chat/list-invoices?limit=50");
  const data = await res.json();

  data.invoices.forEach((invoice) => {
    console.log(`${invoice.filename}: ${invoice.download_url}`);
  });
}

// Preview invoice (base64)
async function previewInvoice(documentId) {
  const res = await fetch(`/chat/get-invoice-content/${documentId}`, {
    method: "POST",
  });
  const data = await res.json();

  // Display in <img>
  document.getElementById("preview").src = data.data_url;
}
```

---

## 🔒 **Security: SAS Token Auto-Expiry**

```python
# Short expiry for download links
download_url = await azure_service.get_blob_download_url(
    blob_name="invoice.png",
    expires_hours=1  # ⏰ Expires after 1 hour
)

# Longer expiry for gallery view
gallery_url = await azure_service.get_blob_download_url(
    blob_name="invoice.png",
    expires_hours=24  # ⏰ Expires after 24 hours
)
```

**After expiry:**

```bash
curl "https://storage.blob.core.windows.net/invoice.png?expired_token"

# Response: AuthenticationFailed
```

---

## 📊 **Architecture:**

```
User → Frontend → Backend API → PostgreSQL (metadata)
                              ↘ Azure Blob Storage (files)
                                      ↓
                           Generate SAS URL (1h expiry)
                                      ↓
Frontend ← Secure URL ← Backend
    ↓
Direct download from Azure (bypass backend)
```

---

## 📝 **Files Created:**

```
✅ AZURE_STORAGE_API_GUIDE.md      # Full documentation
✅ AZURE_API_USAGE.md              # API usage examples
✅ AZURE_STORAGE_SUMMARY.md        # Summary & comparison
✅ AZURE_API_DIAGRAM.txt           # Visual diagrams
✅ AZURE_API_QUICK_REF.md          # This file

✅ services/azure_service.py       # 5 new methods
✅ routes/websocket_chat.py        # 4 new API endpoints
```

---

## 🎯 **Current Status:**

| Component         | Status            | Notes                   |
| ----------------- | ----------------- | ----------------------- |
| **Backend Code**  | ✅ Complete       | All methods implemented |
| **API Endpoints** | ✅ Ready          | 4 endpoints active      |
| **Azure Config**  | ⚠️ Not configured | Need connection string  |
| **Local Storage** | ✅ Working        | Fallback mode           |

---

## 🚀 **Next Steps:**

### **Option 1: Setup Azure (Production)**

1. Create Azure account
2. Create Storage Account
3. Get connection string
4. Add to `.env`:
   ```env
   AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...
   ```
5. Install SDK: `pip install azure-storage-blob`
6. Restart backend
7. Test APIs

### **Option 2: Keep Local (Development)**

- Current setup works fine
- APIs will return error if Azure not configured
- PostgreSQL + local files still functional

---

## ✅ **CONCLUSION:**

**Câu hỏi:** "Nếu lưu lên Azure Storage thì có thể gọi API tới để lấy dữ liệu không?"

**Trả lời:** ✅ **CÓ - Đã có đầy đủ:**

- ✅ 4 API endpoints
- ✅ 5 backend methods
- ✅ SAS token security
- ✅ Auto-expiry protection
- ✅ Base64 preview support
- ✅ Direct download (fast)

**Chỉ cần:** Add Azure credentials vào `.env` là chạy được!

---

**📚 Đọc thêm:**

- `AZURE_STORAGE_API_GUIDE.md` - Full documentation
- `AZURE_API_DIAGRAM.txt` - Visual flows
- `AZURE_STORAGE_SUMMARY.md` - Comparison & recommendations
