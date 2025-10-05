# 🤖 AZURE DOCUMENT INTELLIGENCE - HƯỚNG DẪN SETUP

## 🎯 Tại Sao Dùng Azure Document Intelligence?

### ❌ Vấn Đề Với Tesseract (Hiện Tại):

- ⚠️ Pattern matching cứng nhắc
- ⚠️ Phải define regex cho mỗi field
- ⚠️ Không linh hoạt với format mới
- ⚠️ Confidence thấp (37-50%)
- ⚠️ Nhiều false positive/negative

**Ví dụ:**

```
Pattern: r't[oô]ng.*?(\d{1,3}(?:[,.\s]\d{3})*)'
Chỉ match "tổng cộng", "tống cong", "t0ng c0ng"
Không match: "TOTAL", "Sum", "Grand Total", "Thanh toán"
```

### ✅ Giải Pháp: Azure Document Intelligence

**AI-Powered Extraction:**

- ✅ Tự động nhận diện fields (không cần pattern)
- ✅ Linh hoạt với mọi format hóa đơn
- ✅ Confidence cao (85-95%)
- ✅ Hỗ trợ nhiều ngôn ngữ (Tiếng Việt, English, v.v.)
- ✅ Tự động phát hiện tables, line items
- ✅ Nhiều tổng cộng + grand total

**Ví dụ:**

```
Input: Bất kỳ hóa đơn nào
Output:
  - Invoice ID: ✅ Tự động tìm
  - Amounts: ✅ Tất cả subtotals + grand total
  - Vendor/Customer: ✅ Tự động extract
  - Line Items: ✅ Bảng items với qty, price
```

---

## 📊 So Sánh

| Feature               | Tesseract        | Azure DI          |
| --------------------- | ---------------- | ----------------- |
| **Extraction Method** | Pattern matching | AI-powered        |
| **Flexibility**       | Cứng nhắc        | Linh hoạt 100%    |
| **New Fields**        | Phải code thêm   | Tự động detect    |
| **Confidence**        | 37-50%           | 85-95%            |
| **Line Items**        | Khó extract      | Tự động           |
| **Tables**            | Không hỗ trợ     | ✅ Full support   |
| **Multi-language**    | Limited          | ✅ 50+ languages  |
| **Cost**              | Free             | ~$1.50/1000 pages |
| **Setup**             | Local            | Cloud API         |

---

## 🚀 Cách Setup Azure Document Intelligence

### Bước 1: Tạo Resource Trên Azure Portal

1. **Login Azure:**

   - Truy cập [Azure Portal](https://portal.azure.com)
   - Đăng nhập với tài khoản Microsoft

2. **Tạo Document Intelligence Resource:**

   ```
   1. Click "Create a resource"
   2. Search "Document Intelligence" (hoặc "Form Recognizer")
   3. Click "Create"

   Settings:
   - Subscription: Your Azure subscription
   - Resource Group: DoAnCN-RG (hoặc tạo mới)
   - Region: Southeast Asia
   - Name: doancn-document-intelligence
   - Pricing Tier: Free F0 (1000 pages/month) hoặc S0

   4. Click "Review + Create"
   5. Click "Create"
   ```

3. **Lấy Keys & Endpoint:**
   ```
   1. Vào resource vừa tạo
   2. Sidebar → "Keys and Endpoint"
   3. Copy:
      - KEY 1
      - Endpoint URL
   ```

### Bước 2: Cấu Hình `.env`

Mở file `fastapi_backend\.env`:

```properties
# Azure Document Intelligence (AI Document Intelligence - Flexible Invoice Extraction)
# Get from Azure Portal > Document Intelligence > Keys and Endpoint
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://doancn-document-intelligence.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=YOUR_KEY_HERE
```

**Ví dụ thực tế:**

```properties
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://southeastasia.api.cognitive.microsoft.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

### Bước 3: Install Dependencies

```powershell
cd f:\DoAnCN\fastapi_backend

# Add Azure AI Form Recognizer SDK
poetry add azure-ai-formrecognizer
poetry add azure-core
```

Hoặc với pip:

```powershell
pip install azure-ai-formrecognizer azure-core
```

### Bước 4: Restart Backend

```powershell
cd f:\DoAnCN\fastapi_backend
python main.py
```

Check log:

```
✅ Azure Document Intelligence available
✅ Azure Document Intelligence initialized
```

---

## 🧪 Test Azure DI

### Test 1: Upload Invoice Qua Frontend

1. Start backend với Azure DI configured
2. Upload invoice qua frontend: `http://localhost:3001`
3. Check backend log:

```
🤖 Using Azure Document Intelligence (flexible extraction)
🤖 Running Azure DI on: hoa-don.jpg
✅ Azure DI invoice model successful
✅ Azure DI extraction complete: 15 fields extracted
📊 OCR Result Summary:
   - Method: azure_document_intelligence
   - Confidence: 0.92
```

### Test 2: Compare Results

**Tesseract (Cũ):**

```json
{
  "invoice_code": "1C23MYY",
  "total_amount": "280.000",
  "buyer_name": "CPIIOANGLON",
  "confidence_score": 0.5,
  "extraction_method": "pattern_matching",
  "fields_extracted": ["invoice_code", "amount", "company"]
}
```

**Azure DI (Mới):**

```json
{
  "invoice_code": "1C23MYY",
  "invoice_date": "17/05/2023",
  "total_amount": "280.000",
  "subtotals_list": ["100.000", "180.000"],
  "buyer_name": "CÔNG TY CP HOÀNG LONG",
  "buyer_tax_code": "0123456789",
  "seller_name": "CÔNG TY TNHH ABC",
  "items": [
    {
      "description": "Dịch vụ 1",
      "quantity": 1,
      "unit_price": "100.000",
      "total_price": "100.000"
    },
    {
      "description": "Dịch vụ 2",
      "quantity": 1,
      "unit_price": "180.000",
      "total_price": "180.000"
    }
  ],
  "confidence_score": 0.92,
  "extraction_method": "azure_ai_flexible",
  "fields_extracted": ["invoice_id", "invoice_date", "vendor", "customer", "items", "subtotal", "total_amount", ...]
}
```

**Improvement:**

- ✅ 15 fields thay vì 3
- ✅ Confidence 92% thay vì 50%
- ✅ Line items tự động
- ✅ Subtotals array

---

## 💰 Chi Phí

### Free Tier (F0):

- **1,000 pages/month FREE**
- Sau đó: $10/1,000 pages

### Standard Tier (S0):

- **$1.50/1,000 pages** (prebuilt-invoice/receipt)
- **$1.00/1,000 pages** (general document)

**Ước tính cho project:**

- 100 invoices/ngày = 3,000 invoices/tháng
- Dùng Free Tier: **$0** (nếu <1000 pages)
- Vượt Free Tier: **~$3-5/tháng**

**Rất rẻ so với giá trị!** 🎉

---

## 🔄 Automatic Fallback

Hệ thống tự động fallback khi Azure fail:

```python
# Priority chain:
1. Azure DI Invoice Model
   ↓ (if fail)
2. Azure DI Receipt Model
   ↓ (if fail)
3. Azure DI General Document
   ↓ (if fail)
4. Tesseract Pattern Matching
```

**Log example:**

```
🤖 Using Azure Document Intelligence
⚠️ Invoice model failed, trying receipt model
✅ Azure DI receipt model successful
```

---

## 📋 Supported Models

### 1. `prebuilt-invoice` (Recommended)

**Best for:** Hóa đơn chuyên nghiệp (VAT, B2B)

**Auto-extracts:**

- Invoice ID, Date, Due Date, PO Number
- Vendor: Name, Address, Tax ID, Phone
- Customer: Name, Address, Tax ID
- Line Items: Description, Quantity, Unit, Price, Amount, Tax
- Subtotal, Tax, Discount, Total, Amount Due
- Payment Terms, Currency

### 2. `prebuilt-receipt`

**Best for:** Hóa đơn bán lẻ (siêu thị, nhà hàng)

**Auto-extracts:**

- Merchant: Name, Address, Phone
- Transaction: Date, Time, ID
- Items: Description, Quantity, Price, Total
- Subtotal, Tax, Tip, Total

### 3. `prebuilt-document`

**Best for:** Documents tổng quát

**Auto-extracts:**

- Key-value pairs
- Tables (with headers)
- Text content
- Layout structure

---

## 🎯 Use Cases

### Case 1: Hóa Đơn VAT (Invoice Model)

```
Input: Hóa đơn GTGT chuẩn Việt Nam
Fields extracted:
  ✅ Ký hiệu, số hóa đơn
  ✅ MST người bán/mua
  ✅ Bảng hàng hóa (tên, số lượng, đơn giá, thành tiền)
  ✅ Tiền trước thuế, thuế GTGT, tổng tiền
  ✅ Ngày lập
```

### Case 2: Hóa Đơn Nhà Hàng (Receipt Model)

```
Input: Bill nhà hàng
Fields extracted:
  ✅ Tên nhà hàng, địa chỉ
  ✅ Danh sách món ăn (tên, số lượng, giá)
  ✅ Tạm tính, VAT, tổng cộng
  ✅ Ngày giờ giao dịch
```

### Case 3: Hóa Đơn Tiện Ích (Invoice Model)

```
Input: Hóa đơn điện/nước/gas
Fields extracted:
  ✅ Khách hàng, mã khách hàng
  ✅ Kỳ hóa đơn, chỉ số cũ/mới
  ✅ Mức tiêu thụ, đơn giá
  ✅ Tiền điện, thuế, tổng
```

---

## ⚙️ Configuration Options

### Enable/Disable Azure DI

**Method 1: Environment Variable**

```properties
# Enable
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://...
AZURE_DOCUMENT_INTELLIGENCE_KEY=...

# Disable (fallback to Tesseract)
# AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=
# AZURE_DOCUMENT_INTELLIGENCE_KEY=
```

**Method 2: Code (già config)**

```python
# In ocr_service.py __init__
self.use_azure_di = False  # Force Tesseract
```

### Model Selection Logic

System tự động chọn model dựa trên filename:

```python
def analyze_filename(filename):
    if 'vat' in filename or 'gtgt' in filename:
        return 'invoice'  # → prebuilt-invoice
    elif 'bill' in filename or 'receipt' in filename:
        return 'receipt'  # → prebuilt-receipt
    else:
        return 'general'  # → prebuilt-document
```

---

## 🐛 Troubleshooting

### Error: "Azure DI not configured"

**Solution:**

1. Check `.env` has endpoint & key
2. Restart backend
3. Verify log shows "✅ Azure Document Intelligence initialized"

### Error: "Import azure.ai.formrecognizer failed"

**Solution:**

```powershell
poetry add azure-ai-formrecognizer
# or
pip install azure-ai-formrecognizer
```

### Error: "Unauthorized" or "Invalid key"

**Solution:**

1. Verify KEY copied correctly (no spaces)
2. Verify endpoint URL correct (với trailing `/`)
3. Check resource not deleted on Azure Portal

### Low Confidence (<60%)

**Possible causes:**

- Image quality too low (blur, skew)
- Non-standard format
- Wrong model selected

**Solutions:**

- Improve image preprocessing
- Try different model
- Use general document model

---

## 📈 Performance

### Response Time:

- **Tesseract:** 2-5 seconds (local)
- **Azure DI:** 3-8 seconds (cloud API call)

### Accuracy:

- **Tesseract:** 50-70% (depends on pattern quality)
- **Azure DI:** 85-95% (AI-powered)

### Throughput:

- **Tesseract:** Unlimited (local)
- **Azure DI:** 15 requests/second (S0 tier)

---

## ✅ Checklist Setup

- [ ] Tạo Azure Document Intelligence resource
- [ ] Copy endpoint và key
- [ ] Update file `.env`
- [ ] Install dependencies (`azure-ai-formrecognizer`)
- [ ] Restart backend
- [ ] Verify log: "✅ Azure DI initialized"
- [ ] Upload test invoice
- [ ] Check extraction results
- [ ] Compare với Tesseract
- [ ] Monitor usage/cost trên Azure Portal

---

## 🎯 Kết Luận

**Azure Document Intelligence là game-changer!** 🚀

**Lợi ích:**

- ✅ Flexible extraction (không cần code pattern)
- ✅ High accuracy (85-95%)
- ✅ Auto-detect line items + tables
- ✅ Nhiều tổng cộng + grand total
- ✅ Multi-language support
- ✅ Fallback to Tesseract nếu Azure fail

**Chi phí:** ~$3-5/tháng cho 3000 invoices

**ROI:** Tiết kiệm 10+ giờ code pattern matching mỗi tháng!

---

## 📞 Support

**Documentation:**

- [Azure Document Intelligence Docs](https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/)
- [Python SDK Reference](https://learn.microsoft.com/en-us/python/api/azure-ai-formrecognizer/)

**Pricing:**

- [Azure Document Intelligence Pricing](https://azure.microsoft.com/en-us/pricing/details/form-recognizer/)

**Quota & Limits:**

- Free (F0): 1,000 pages/month
- Standard (S0): Unlimited, pay-as-you-go
