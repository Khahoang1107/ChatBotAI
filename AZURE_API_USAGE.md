# 🚀 Azure Storage API - Hướng Dẫn Sử Dụng

## ✅ **Code đã được thêm vào hệ thống!**

---

## 📋 **Các API mới đã thêm:**

### **1. Download Invoice (Secure SAS URL)**

```http
GET /chat/download-invoice/{document_id}
```

**Parameters:**

- `document_id` (path): ID của document trong PostgreSQL

**Response:**

```json
{
  "success": true,
  "document_id": 9,
  "filename": "hoa-don-ban-hang.png",
  "invoice_type": "food_service",
  "download_url": "https://chatbotinvoices.blob.core.windows.net/chat-documents/session_abc/uuid.png?sv=2021-06-08&se=2025-10-03T22%3A00%3A00Z&sr=b&sp=r&sig=ABC123...",
  "expires_in": "1 hour"
}
```

**Frontend Usage:**

```javascript
// React/Vue/Angular
async function downloadInvoice(documentId) {
  const response = await fetch(`/chat/download-invoice/${documentId}`);
  const data = await response.json();

  if (data.success) {
    // Option 1: Open in new tab
    window.open(data.download_url, "_blank");

    // Option 2: Download as file
    const link = document.createElement("a");
    link.href = data.download_url;
    link.download = data.filename;
    link.click();

    // Option 3: Display in <img>
    document.getElementById("invoice-preview").src = data.download_url;
  }
}
```

**Curl Test:**

```bash
curl http://localhost:8000/chat/download-invoice/9
```

---

### **2. List All Invoices**

```http
GET /chat/list-invoices?session_id={optional}&limit={optional}
```

**Parameters:**

- `session_id` (query, optional): Filter by session
- `limit` (query, optional): Max results (default 100)

**Response:**

```json
{
  "success": true,
  "count": 10,
  "invoices": [
    {
      "id": 10,
      "filename": "3-24-2020 10-45-20 AM.png",
      "invoice_type": "general",
      "uploaded_at": "2025-10-03T20:46:37",
      "session_id": "17ae1e1a05f85ebe",
      "download_url": "https://...?SAS_TOKEN"
    },
    {
      "id": 9,
      "filename": "hoa-don-ban-hang.png",
      "invoice_type": "food_service",
      "uploaded_at": "2025-10-03T20:44:49",
      "session_id": "6b2075ed012de3cc",
      "download_url": "https://...?SAS_TOKEN"
    }
  ]
}
```

**Frontend Usage:**

```javascript
// Display invoice list
async function loadInvoiceList() {
  const response = await fetch("/chat/list-invoices?limit=50");
  const data = await response.json();

  const invoiceList = document.getElementById("invoice-list");

  data.invoices.forEach((invoice) => {
    const item = document.createElement("div");
    item.innerHTML = `
      <div class="invoice-card">
        <img src="${invoice.download_url}" alt="${invoice.filename}" />
        <h3>${invoice.filename}</h3>
        <p>Type: ${invoice.invoice_type}</p>
        <p>Date: ${new Date(invoice.uploaded_at).toLocaleDateString()}</p>
        <button onclick="downloadInvoice(${invoice.id})">Download</button>
      </div>
    `;
    invoiceList.appendChild(item);
  });
}
```

**Curl Test:**

```bash
# List all
curl http://localhost:8000/chat/list-invoices

# Filter by session
curl http://localhost:8000/chat/list-invoices?session_id=6b2075ed012de3cc

# Limit results
curl http://localhost:8000/chat/list-invoices?limit=5
```

---

### **3. Get Invoice Content (Base64)**

```http
POST /chat/get-invoice-content/{document_id}
```

**Response:**

```json
{
  "success": true,
  "document_id": 9,
  "filename": "hoa-don-ban-hang.png",
  "content_type": "image/png",
  "size": 163176,
  "content_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "data_url": "data:image/png;base64,iVBORw0KGgo..."
}
```

**Frontend Usage:**

```javascript
// Display image directly without download
async function previewInvoice(documentId) {
  const response = await fetch(`/chat/get-invoice-content/${documentId}`, {
    method: "POST",
  });
  const data = await response.json();

  // Option 1: Use data_url directly
  document.getElementById("invoice-preview").src = data.data_url;

  // Option 2: Build data URL manually
  const dataUrl = `data:${data.content_type};base64,${data.content_base64}`;
  document.getElementById("invoice-preview").src = dataUrl;
}
```

**Use Cases:**

- Image preview trong modal
- OCR processing trong backend
- Email attachment (convert base64 to file)
- Canvas manipulation

**Curl Test:**

```bash
curl -X POST http://localhost:8000/chat/get-invoice-content/9 > invoice_response.json
```

---

### **4. List Azure Blobs Directly**

```http
GET /chat/list-azure-blobs?session_id={optional}
```

**Response:**

```json
{
  "success": true,
  "count": 2,
  "blobs": [
    {
      "name": "session_abc/uuid1.png",
      "size": 163176,
      "last_modified": "2025-10-03T20:44:49",
      "content_type": "image/png"
    },
    {
      "name": "session_abc/uuid2.png",
      "size": 196038,
      "last_modified": "2025-10-03T20:46:37",
      "content_type": "image/png"
    }
  ]
}
```

**Curl Test:**

```bash
curl http://localhost:8000/chat/list-azure-blobs
```

---

## 🔧 **Backend Methods Added:**

### **In `services/azure_service.py`:**

```python
# 1. Generate secure download URL
download_url = await azure_service.get_blob_download_url(
    blob_name="session_abc/invoice.png",
    expires_hours=24  # URL hết hạn sau 24h
)

# 2. Download file content
file_bytes = await azure_service.download_blob_content(
    blob_name="session_abc/invoice.png"
)

# 3. List blobs (optionally filter by session)
blobs = await azure_service.list_user_blobs(
    session_id="session_abc"  # Optional filter
)

# 4. Get blob properties (size, last modified, etc.)
properties = await azure_service.get_blob_properties(
    blob_name="session_abc/invoice.png"
)
```

---

## 🧪 **TESTING WORKFLOW:**

### **Scenario 1: Upload → Download**

```bash
# 1. Upload invoice
curl -X POST http://localhost:8000/chat/upload \
  -F "file=@invoice.png"

# Response: {"document_id": 11, ...}

# 2. Get download URL
curl http://localhost:8000/chat/download-invoice/11

# Response: {"download_url": "https://...?SAS_TOKEN", ...}

# 3. Download file (paste URL in browser or use wget)
wget "https://chatbotinvoices.blob.core.windows.net/chat-documents/...?SAS_TOKEN" -O downloaded_invoice.png
```

### **Scenario 2: List → Preview → Download**

```bash
# 1. List all invoices
curl http://localhost:8000/chat/list-invoices

# Response: {"invoices": [{id: 9, ...}, {id: 10, ...}]}

# 2. Preview invoice (base64)
curl -X POST http://localhost:8000/chat/get-invoice-content/9

# Response: {"data_url": "data:image/png;base64,..."}
# Copy data_url và paste vào browser address bar để xem ảnh

# 3. Download specific invoice
curl http://localhost:8000/chat/download-invoice/9
```

---

## 🔒 **SECURITY FEATURES:**

### **SAS Token với Auto-Expiry:**

```python
# Download URL (expires in 1 hour)
download_url = await azure_service.get_blob_download_url(
    blob_name="invoice.png",
    expires_hours=1  # ⏰ URL tự động hết hạn sau 1 giờ
)

# List view URLs (expires in 24 hours)
list_url = await azure_service.get_blob_download_url(
    blob_name="invoice.png",
    expires_hours=24  # ⏰ Lâu hơn cho list view
)
```

**After expiry:**

```bash
# Try to access expired URL:
curl "https://...?expired_sas_token"

# Response:
<?xml version="1.0" encoding="utf-8"?>
<Error>
  <Code>AuthenticationFailed</Code>
  <Message>Server failed to authenticate the request. The signed resource is not allowed for the this resource level.</Message>
</Error>
```

**✅ Benefits:**

- Không cần manually revoke URLs
- Tự động bảo vệ sau expiry time
- Generate URL mới mỗi khi request (fresh token)

---

## 📊 **DATABASE vs AZURE:**

### **PostgreSQL (DocumentStorage):**

```sql
SELECT id, filename, invoice_type, uploaded_at, file_path
FROM document_storage
ORDER BY uploaded_at DESC;
```

**Lưu:**

- Metadata (filename, type, date)
- `file_path` = blob_name trong Azure (e.g., "session_abc/uuid.png")
- **KHÔNG lưu full URL** (để có thể generate SAS token mới mỗi lần)

### **Azure Blob Storage:**

```
Container: chat-documents
├── session_6b2075ed012de3cc/
│   └── uuid1.png (163 KB)
└── session_17ae1e1a05f85ebe/
    └── uuid2.png (196 KB)
```

**Lưu:**

- File gốc (bytes)
- Metadata (content-type, last-modified)
- No structured data (chỉ có files)

---

## 💡 **BEST PRACTICES:**

### ✅ **DO:**

```python
# 1. Generate URL on-demand
@router.get("/download/{doc_id}")
async def download(doc_id: int):
    # ✅ Generate fresh SAS URL
    url = await azure_service.get_blob_download_url(blob_name, expires_hours=1)
    return {"download_url": url}

# 2. Short expiry cho sensitive data
download_url = await azure_service.get_blob_download_url(
    blob_name="confidential_invoice.pdf",
    expires_hours=1  # ✅ 1 hour cho download links
)

# 3. Store blob_name, not full URL
db.add(DocumentStorage(
    filename="invoice.png",
    file_path="session_abc/uuid.png"  # ✅ Only blob_name
))
```

### ❌ **DON'T:**

```python
# 1. NEVER lưu full URL vào database
db.add(DocumentStorage(
    azure_url="https://...?sas_token"  # ❌ Token sẽ expire!
))

# 2. NEVER public access cho sensitive files
container.set_container_access_policy(
    public_access='blob'  # ❌ Ai cũng xem được!
)

# 3. NEVER long expiry cho download links
url = await azure_service.get_blob_download_url(
    blob_name,
    expires_hours=8760  # ❌ 1 year?! Nguy hiểm!
)
```

---

## 🎯 **RECOMMENDED ARCHITECTURE:**

```
User Request
    ↓
Frontend API Call
    ↓
Backend Route (/download-invoice/{id})
    ↓
1. Query PostgreSQL (get file_path)
    ↓
2. Generate SAS URL (expires in 1h)
    ↓
3. Return URL to frontend
    ↓
Frontend receives URL
    ↓
Direct download from Azure
(bypasses backend - faster!)
```

**✅ Benefits:**

- Backend không phải stream large files
- Azure CDN tự động cache
- Secure với SAS token auto-expiry
- Scalable (Azure handles bandwidth)

---

## 📝 **SUMMARY:**

| API Endpoint                | Purpose            | Expiry   | Use Case           |
| --------------------------- | ------------------ | -------- | ------------------ |
| `/download-invoice/{id}`    | Get download URL   | 1 hour   | User downloads     |
| `/list-invoices`            | List all with URLs | 24 hours | Gallery view       |
| `/get-invoice-content/{id}` | Get base64 content | N/A      | Preview/Processing |
| `/list-azure-blobs`         | Direct Azure list  | N/A      | Admin/Debug        |

**✅ Tất cả APIs đã sẵn sàng! Chỉ cần:**

1. Setup Azure Storage account
2. Add connection string vào `.env`
3. Test APIs với curl/Postman
4. Integrate vào frontend

**Bạn muốn tôi giúp setup Azure account không?** 🚀
