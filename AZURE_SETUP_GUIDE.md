# 🔐 HƯỚNG DẪN CẤU HÌNH AZURE STORAGE

## ❓ Tại Sao Không Lưu Lên Azure?

**Nguyên nhân:** File `.env` thiếu cấu hình Azure Storage credentials.

**Hiện trạng:**

- ✅ **OCR vẫn hoạt động** - Dùng Tesseract local
- ✅ **Dữ liệu vẫn được lưu** - Vào PostgreSQL + RAG
- ❌ **Không lưu lên Azure Cloud** - Thiếu connection string

## 📋 Bước 1: Tạo Azure Storage Account

### Cách 1: Azure Portal (Web)

1. Truy cập [Azure Portal](https://portal.azure.com)
2. Tạo Storage Account:

   - Click **"Create a resource"**
   - Chọn **"Storage Account"**
   - Điền thông tin:
     ```
     Resource Group: DoAnCN-RG (hoặc tạo mới)
     Storage Account Name: doancninvoice (phải unique)
     Region: Southeast Asia
     Performance: Standard
     Redundancy: LRS (cheapest)
     ```
   - Click **"Review + Create"**

3. Lấy Connection String:
   - Vào Storage Account vừa tạo
   - Sidebar → **"Access Keys"**
   - Copy **"Connection string"** từ key1

### Cách 2: Azure CLI (Terminal)

```bash
# Login
az login

# Tạo Resource Group
az group create --name DoAnCN-RG --location southeastasia

# Tạo Storage Account
az storage account create \
  --name doancninvoice \
  --resource-group DoAnCN-RG \
  --location southeastasia \
  --sku Standard_LRS

# Lấy Connection String
az storage account show-connection-string \
  --name doancninvoice \
  --resource-group DoAnCN-RG \
  --output tsv
```

## 📋 Bước 2: Cấu Hình `.env`

Mở file `fastapi_backend\.env` và điền:

```properties
# Azure Storage Configuration
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=doancninvoice;AccountKey=YOUR_KEY_HERE;EndpointSuffix=core.windows.net
AZURE_CONTAINER_NAME=chat-documents

# Azure Computer Vision (Optional)
AZURE_CV_ENDPOINT=https://southeastasia.api.cognitive.microsoft.com/
AZURE_CV_KEY=YOUR_COMPUTER_VISION_KEY
```

**Lưu ý:**

- `AZURE_STORAGE_CONNECTION_STRING` là bắt buộc để upload
- `AZURE_CV_*` là optional (dùng cho Azure OCR thay vì Tesseract)

## 📋 Bước 3: Khởi Động Lại Backend

```powershell
cd f:\DoAnCN\fastapi_backend
poetry run python main.py
```

Kiểm tra log:

```
✅ Created Azure container: chat-documents
```

## 🧪 Test Upload

1. Upload invoice qua frontend
2. Check backend log:

   ```
   ☁️ Uploaded to Azure: https://doancninvoice.blob.core.windows.net/chat-documents/...
   ```

3. Xem file trên Azure Portal:
   - Storage Account → Containers → chat-documents

## 💰 Chi Phí Azure

**Free Tier (12 tháng đầu):**

- 5 GB Blob Storage
- 20,000 read operations
- 2,000 write operations

**Sau Free Tier:**

- ~$0.02/GB/tháng cho LRS
- ~$0.0004/10,000 operations

**Ước tính:**

- 1000 invoices (~50 MB) = **$0.001/tháng**
- Rất rẻ! 🎉

## 🔄 Alternative: Không Dùng Azure

Nếu không cần cloud storage:

**Hệ thống vẫn hoạt động bình thường:**

- ✅ OCR dùng Tesseract (local)
- ✅ Ảnh lưu trong `uploads/` folder
- ✅ Metadata lưu PostgreSQL
- ✅ RAG semantic search hoạt động
- ✅ Chatbot trả lời câu hỏi

**Chỉ thiếu:**

- ❌ Không backup ảnh lên cloud
- ❌ Không access ảnh từ nhiều máy

## ⚠️ Lưu Ý Bảo Mật

**TUYỆT ĐỐI KHÔNG:**

- ❌ Commit `.env` lên Git
- ❌ Share connection string publicly
- ❌ Hard-code keys vào code

**NÊN:**

- ✅ Add `.env` vào `.gitignore`
- ✅ Dùng Azure Key Vault cho production
- ✅ Rotate keys định kỳ

## 📞 Support

**Nếu gặp lỗi:**

```python
# Error: Azure Storage not configured
⚠️ Azure upload failed (non-critical): Azure Storage not configured
```

**Giải pháp:**

1. Check file `.env` có `AZURE_STORAGE_CONNECTION_STRING`
2. Connection string phải đúng format
3. Storage account phải tồn tại trên Azure

**Test connection:**

```python
from azure.storage.blob import BlobServiceClient

conn_str = "YOUR_CONNECTION_STRING"
blob_service = BlobServiceClient.from_connection_string(conn_str)

# List containers
for container in blob_service.list_containers():
    print(container.name)
```

## ✅ Checklist

- [ ] Tạo Azure Storage Account
- [ ] Lấy Connection String
- [ ] Update file `.env`
- [ ] Restart backend
- [ ] Test upload invoice
- [ ] Verify file trên Azure Portal

## 🎯 Tóm Tắt

**Hiện tại:** Hệ thống hoạt động, chỉ thiếu Azure cloud backup.

**Để lưu lên Azure:** Cấu hình `.env` với Azure credentials.

**Nếu không cần Azure:** Không làm gì cả, hệ thống vẫn OK! ✅
