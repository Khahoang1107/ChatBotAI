# 🌐 Azure Storage API - Hướng Dẫn Truy Xuất Dữ Liệu

## ✅ **CÂU TRẢ LỜI: CÓ - Có 4 cách lấy dữ liệu từ Azure Storage!**

---

## 📋 **Các cách truy cập Azure Storage:**

### **1️⃣ DIRECT URL (Public Access)**

**Cách đơn giản nhất - Truy cập trực tiếp qua HTTPS**

```bash
# URL format:
https://{storage_account}.blob.core.windows.net/{container}/{blob_name}

# Ví dụ thực tế:
https://chatbotinvoices.blob.core.windows.net/chat-documents/session_abc123/invoice_001.png
```

**✅ Ưu điểm:**

- Không cần authentication
- Truy cập từ browser, mobile app, bất kỳ đâu
- Tốc độ cao (Azure CDN)
- Đơn giản cho public files

**❌ Nhược điểm:**

- **BẤT AN TOÀN** cho dữ liệu nhạy cảm (ai cũng xem được nếu có link)
- Không kiểm soát được quyền truy cập

**⚠️ Phù hợp cho:** Public images, marketing materials, static files

---

### **2️⃣ SAS TOKEN (Shared Access Signature) ⭐ KHUYẾN NGHỊ**

**Truy cập BẢO MẬT với token có thời hạn**

```python
# Code để generate SAS URL:
from azure.storage.blob import generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta

def get_secure_blob_url(blob_name: str, expires_in_hours: int = 24):
    """Tạo URL có SAS token (tự động expire)"""

    # Tạo SAS token với quyền READ, hết hạn sau 24h
    sas_token = generate_blob_sas(
        account_name=storage_account_name,
        container_name="chat-documents",
        blob_name=blob_name,
        account_key=storage_account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=expires_in_hours)
    )

    # URL có token
    return f"https://{storage_account_name}.blob.core.windows.net/chat-documents/{blob_name}?{sas_token}"

# Sử dụng:
secure_url = get_secure_blob_url("session_abc/invoice.png", expires_in_hours=1)
# → URL này CHỈ hoạt động trong 1 giờ, sau đó tự động hết hạn
```

**✅ Ưu điểm:**

- **BẢO MẬT CAO** - Token tự động expire
- Kiểm soát quyền (read-only, read-write, delete, etc.)
- Không lộ storage account key
- Audit trail (track ai truy cập)

**✅ Use Cases:**

- Hóa đơn khách hàng (nhạy cảm)
- Documents cần authentication
- Temporary file sharing
- Download links qua email

**💡 Best Practice:**

```python
# Short expiry cho download links
download_link = get_secure_blob_url("invoice.pdf", expires_in_hours=1)

# Longer expiry cho embedded images
image_url = get_secure_blob_url("logo.png", expires_in_hours=24)
```

---

### **3️⃣ AZURE BLOB SDK (Python Backend)**

**Truy cập programmatic từ backend service**

```python
from azure.storage.blob import BlobServiceClient

async def download_blob_from_azure(blob_name: str) -> bytes:
    """Download file content từ Azure Storage"""

    blob_service_client = BlobServiceClient.from_connection_string(
        AZURE_STORAGE_CONNECTION_STRING
    )

    blob_client = blob_service_client.get_blob_client(
        container="chat-documents",
        blob=blob_name
    )

    # Download file as bytes
    blob_data = blob_client.download_blob()
    file_content = blob_data.readall()

    return file_content

# Sử dụng:
invoice_bytes = await download_blob_from_azure("session_abc/invoice.png")

# Hoặc lưu ra file:
with open("downloaded_invoice.png", "wb") as f:
    f.write(invoice_bytes)
```

**API Methods có sẵn:**

```python
# 1. Download blob content
blob_data = blob_client.download_blob().readall()

# 2. Get blob properties (metadata, size, last modified)
properties = blob_client.get_blob_properties()
print(f"Size: {properties.size} bytes")
print(f"Content Type: {properties.content_settings.content_type}")
print(f"Last Modified: {properties.last_modified}")

# 3. Check if blob exists
exists = blob_client.exists()

# 4. Delete blob
blob_client.delete_blob()

# 5. List all blobs in container
container_client = blob_service_client.get_container_client("chat-documents")
blob_list = container_client.list_blobs()
for blob in blob_list:
    print(f"Blob: {blob.name}, Size: {blob.size}")

# 6. Get blob metadata
metadata = blob_client.get_blob_properties().metadata
```

**✅ Ưu điểm:**

- Full control từ backend
- Không expose URL ra ngoài
- Có thể xử lý file trước khi trả về client
- Audit và logging tốt

**Use Cases:**

- Backend processing (resize images, OCR, etc.)
- Secure file serving through API gateway
- Data migration/backup

---

### **4️⃣ REST API (Azure Storage REST API)**

**Gọi trực tiếp Azure REST endpoints**

```python
import requests
from datetime import datetime, timedelta

def get_blob_via_rest_api(blob_name: str, sas_token: str):
    """Gọi Azure REST API để lấy blob"""

    url = f"https://{account_name}.blob.core.windows.net/chat-documents/{blob_name}?{sas_token}"

    headers = {
        "x-ms-version": "2021-06-08",
        "x-ms-date": datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.content  # File bytes
    else:
        raise Exception(f"Failed to download: {response.status_code}")

# Sử dụng:
file_bytes = get_blob_via_rest_api("invoice.png", sas_token)
```

**Available REST Endpoints:**

```bash
# Get Blob
GET https://{account}.blob.core.windows.net/{container}/{blob}

# List Blobs
GET https://{account}.blob.core.windows.net/{container}?restype=container&comp=list

# Get Blob Properties
HEAD https://{account}.blob.core.windows.net/{container}/{blob}

# Delete Blob
DELETE https://{account}.blob.core.windows.net/{container}/{blob}

# Upload Blob
PUT https://{account}.blob.core.windows.net/{container}/{blob}
```

---

## 🏗️ **KIẾN TRÚC HỆ THỐNG CỦA BẠN:**

### **Hiện tại (chưa có Azure):**

```
User → Frontend → Backend API → Local Storage (uploads/)
                                      ↓
                                PostgreSQL (metadata only)
```

### **Sau khi dùng Azure Storage:**

```
User → Frontend → Backend API → Azure Blob Storage (files)
                      ↓                    ↓
                PostgreSQL          (secure URLs)
              (metadata + Azure URL)       ↓
                      ↓                    ↓
                Frontend/User ← SAS URL ← API
```

---

## 💻 **CODE MẪU CHO PROJECT CỦA BẠN:**

### **Thêm vào `services/azure_service.py`:**

```python
async def get_blob_download_url(self, blob_name: str, expires_hours: int = 24) -> str:
    """Generate secure download URL with SAS token"""
    try:
        if not self.blob_service_client:
            raise Exception("Azure Storage not configured")

        from azure.storage.blob import generate_blob_sas, BlobSasPermissions
        from datetime import datetime, timedelta

        # Generate SAS token
        sas_token = generate_blob_sas(
            account_name=self.blob_service_client.account_name,
            container_name=self.container_name,
            blob_name=blob_name,
            account_key=self.blob_service_client.credential.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=expires_hours)
        )

        # Build secure URL
        url = f"https://{self.blob_service_client.account_name}.blob.core.windows.net/{self.container_name}/{blob_name}?{sas_token}"

        logger.info(f"✅ Generated SAS URL (expires in {expires_hours}h): {blob_name}")
        return url

    except Exception as e:
        logger.error(f"❌ Failed to generate SAS URL: {e}")
        raise

async def download_blob_content(self, blob_name: str) -> bytes:
    """Download blob content as bytes"""
    try:
        if not self.blob_service_client:
            raise Exception("Azure Storage not configured")

        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name,
            blob=blob_name
        )

        blob_data = blob_client.download_blob()
        content = blob_data.readall()

        logger.info(f"✅ Downloaded blob: {blob_name} ({len(content)} bytes)")
        return content

    except Exception as e:
        logger.error(f"❌ Failed to download blob: {e}")
        raise

async def list_user_blobs(self, session_id: str = None) -> List[Dict]:
    """List all blobs (optionally filter by session_id)"""
    try:
        if not self.blob_service_client:
            raise Exception("Azure Storage not configured")

        container_client = self.blob_service_client.get_container_client(
            self.container_name
        )

        blob_list = []
        prefix = f"{session_id}/" if session_id else None

        for blob in container_client.list_blobs(name_starts_with=prefix):
            blob_list.append({
                "name": blob.name,
                "size": blob.size,
                "last_modified": blob.last_modified.isoformat(),
                "content_type": blob.content_settings.content_type if blob.content_settings else None
            })

        logger.info(f"✅ Listed {len(blob_list)} blobs")
        return blob_list

    except Exception as e:
        logger.error(f"❌ Failed to list blobs: {e}")
        return []
```

### **Thêm API Endpoints vào `routes/websocket_chat.py`:**

```python
@router.get("/download-invoice/{document_id}")
async def download_invoice_from_azure(document_id: int, db: Session = Depends(get_db)):
    """API để download hóa đơn từ Azure Storage"""

    # 1. Get document from database
    document = db.query(DocumentStorage).filter(DocumentStorage.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # 2. Parse blob_name from file_path
    # file_path format: "session_abc/uuid.png"
    blob_name = document.file_path

    # 3. Generate secure download URL (expires in 1 hour)
    download_url = await azure_service.get_blob_download_url(blob_name, expires_hours=1)

    return {
        "success": True,
        "document_id": document_id,
        "filename": document.filename,
        "download_url": download_url,
        "expires_in": "1 hour"
    }

@router.get("/list-invoices")
async def list_all_invoices(session_id: str = None, db: Session = Depends(get_db)):
    """API để list tất cả hóa đơn đã lưu"""

    # Option 1: From PostgreSQL (faster, có metadata)
    query = db.query(DocumentStorage)
    if session_id:
        query = query.filter(DocumentStorage.session_id == session_id)

    documents = query.order_by(DocumentStorage.uploaded_at.desc()).all()

    result = []
    for doc in documents:
        # Generate download URL cho mỗi document
        download_url = await azure_service.get_blob_download_url(
            doc.file_path,
            expires_hours=24
        )

        result.append({
            "id": doc.id,
            "filename": doc.filename,
            "invoice_type": doc.invoice_type,
            "uploaded_at": doc.uploaded_at.isoformat(),
            "download_url": download_url  # Secure URL with 24h expiry
        })

    return {
        "success": True,
        "count": len(result),
        "invoices": result
    }

@router.post("/get-invoice-content/{document_id}")
async def get_invoice_file_content(document_id: int, db: Session = Depends(get_db)):
    """API để lấy file content trực tiếp (để process trong backend)"""

    document = db.query(DocumentStorage).filter(DocumentStorage.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Download file content từ Azure
    file_bytes = await azure_service.download_blob_content(document.file_path)

    # Return as base64 để frontend có thể display
    import base64
    file_base64 = base64.b64encode(file_bytes).decode('utf-8')

    return {
        "success": True,
        "filename": document.filename,
        "content_type": "image/png",  # or detect from filename
        "size": len(file_bytes),
        "content_base64": file_base64  # Frontend có thể dùng: data:image/png;base64,{content}
    }
```

---

## 🧪 **TEST APIs:**

### **1. Upload invoice (existing):**

```bash
curl -X POST http://localhost:8000/chat/upload \
  -F "file=@invoice.png"
```

### **2. List all invoices:**

```bash
curl http://localhost:8000/chat/list-invoices

# Response:
{
  "success": true,
  "count": 10,
  "invoices": [
    {
      "id": 9,
      "filename": "hoa-don-ban-hang.png",
      "invoice_type": "food_service",
      "uploaded_at": "2025-10-03T20:44:49",
      "download_url": "https://chatbotinvoices.blob.core.windows.net/chat-documents/session_abc/uuid.png?SAS_TOKEN"
    }
  ]
}
```

### **3. Download specific invoice:**

```bash
curl http://localhost:8000/chat/download-invoice/9

# Response:
{
  "success": true,
  "document_id": 9,
  "filename": "hoa-don-ban-hang.png",
  "download_url": "https://...?sas_token",
  "expires_in": "1 hour"
}
```

### **4. Get file content directly:**

```bash
curl -X POST http://localhost:8000/chat/get-invoice-content/9

# Response:
{
  "content_base64": "iVBORw0KGgo..."  # Use in <img src="data:image/png;base64,..." />
}
```

---

## 🔒 **BẢO MẬT:**

### **❌ KHÔNG NÊN (Public URL):**

```python
# Direct public URL - AI CŨng xem được!
public_url = "https://storage.blob.core.windows.net/invoices/secret_invoice.png"
```

### **✅ NÊN DÙNG (SAS Token):**

```python
# SAS URL với expiry 1 giờ
sas_url = "https://storage.blob.core.windows.net/invoices/invoice.png?sv=2021-06-08&se=2025-10-03T22%3A00%3A00Z&sr=b&sp=r&sig=ABC123..."

# Sau 1 giờ → URL này TỰ ĐỘNG không hoạt động nữa
```

### **Best Practices:**

1. **Luôn dùng SAS token cho private data**
2. **Short expiry** cho download links (1-24h)
3. **Store blob_name trong PostgreSQL**, không store full URL
4. **Generate URL on-demand** khi user request
5. **Audit logging** - track ai download gì, khi nào

---

## 📊 **SO SÁNH:**

| Phương pháp     | Bảo mật    | Tốc độ        | Use Case       | Độ phức tạp     |
| --------------- | ---------- | ------------- | -------------- | --------------- |
| **Public URL**  | ❌ Thấp    | ⚡ Nhanh nhất | Public files   | ⭐ Đơn giản     |
| **SAS Token**   | ✅ Cao     | ⚡ Nhanh      | Private files  | ⭐⭐ Vừa        |
| **Backend SDK** | ✅ Rất cao | 🐢 Chậm hơn   | Processing     | ⭐⭐⭐ Phức tạp |
| **REST API**    | ✅ Cao     | ⚡ Nhanh      | Cross-platform | ⭐⭐ Vừa        |

---

## 🎯 **KHUYẾN NGHỊ CHO PROJECT:**

**Kiến trúc tốt nhất:**

```python
# 1. Upload → Lưu vào Azure + PostgreSQL
upload_result = await azure_service.upload_image_to_azure(...)
db.add(DocumentStorage(
    filename=...,
    file_path=upload_result['blob_name'],  # Chỉ lưu blob_name
    azure_url=None  # KHÔNG lưu full URL
))

# 2. Khi cần download → Generate SAS URL on-demand
download_url = await azure_service.get_blob_download_url(
    blob_name=document.file_path,
    expires_hours=1  # Short expiry
)

# 3. Return URL cho frontend
return {"download_url": download_url}

# 4. Frontend dùng URL này trong 1 giờ, sau đó expire tự động
```

**✅ Lợi ích:**

- Bảo mật cao (URL tự động expire)
- Không lưu URL cũ trong database
- Flexible (có thể thay đổi storage account mà không update DB)
- Audit trail (track mỗi lần generate URL)

---

## 💡 **Tôi có thể:**

1. **Thêm các API methods vào `azure_service.py`** (get_blob_download_url, download_blob_content, list_user_blobs)
2. **Tạo API endpoints mới** (/download-invoice, /list-invoices, /get-invoice-content)
3. **Update database model** để lưu blob_name thay vì full URL
4. **Viết test cases** để verify Azure APIs hoạt động

**Bạn muốn tôi implement không?** 🚀
