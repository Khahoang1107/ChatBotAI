# Quick Test Guide - Upload Flow Verification

## Prerequisites

- ✅ Backend running on port 8000
- ✅ Chatbot running on port 5001
- ✅ Frontend running on port 5173/5174
- ✅ Frontend code fixed (processFiles now calls backend)

## Quick Test Steps

### Step 1: Open Browser Dev Tools

```
Press F12 → Go to Console tab
```

### Step 2: Access Frontend

```
http://localhost:5173
or
http://localhost:5174
```

### Step 3: Upload Image

**Option A: Camera Upload**

1. Click camera icon 📷
2. Allow camera access
3. Take photo
4. Watch the magic happen! ✨

**Option B: File Upload**

1. Click upload button 📁
2. Select invoice image (JPG/PNG)
3. Watch the magic happen! ✨

### Step 4: Expected Console Output

#### Browser Console (F12):

```javascript
Processing files: [File {name: "invoice.jpg", ...}]
// Then after fetch completes:
// No errors ✅
```

#### Backend Terminal:

```
📤 Chat upload: invoice_12345.jpg
OCR extraction started...
Azure upload started...
Azure URL: https://...blob.core.windows.net/...
Saving to DocumentStorage table...
Processing document for RAG: doc_12345
Added 3 chunks to RAG database
RAG stats: {'total_documents': 1, 'collection_size': 3}
Upload complete ✅
```

#### Chatbot Terminal:

```
(Should not receive file directly anymore - frontend handles upload first)
```

### Step 5: Expected Frontend Chat Messages

**Message 1 (Immediate):**

```
📤 Đã nhận 1 file:
• invoice.jpg (125.3KB)

Đang xử lý OCR và lưu vào hệ thống...
```

**Message 2 (After processing ~3-5 seconds):**

```
✅ Đã xử lý xong: invoice.jpg

📝 Kết quả OCR:
[Extracted text from invoice will appear here]

💾 Đã lưu vào hệ thống RAG và Azure Storage
🔗 URL: https://storageaccountnam8ab3.blob.core.windows.net/uploads/invoice_12345.jpg
```

### Step 6: Test RAG Query

**Type in chat:**

```
xem dữ liệu hóa đơn
```

**Expected response:**

```
[Bot responds with intelligent summary of uploaded invoices using Google AI]

Example:
"Dựa trên dữ liệu từ hệ thống, tôi tìm thấy 1 hóa đơn:

- Hóa đơn: invoice.jpg
- Số hóa đơn: INV-001
- Ngày: 2024-01-15
- Tổng tiền: $1,250.00
- Nội dung: [summary of invoice items]

Bạn có muốn xem chi tiết hóa đơn nào không?"
```

## Verification Commands

### Check Backend Health

```powershell
curl http://localhost:8000/health
# Expected: {"status":"healthy","timestamp":"..."}
```

### Check RAG Stats

```powershell
curl http://localhost:8000/chat/stats
# Expected: {"total_documents": 1, "recent_documents": [...]}
```

### Check ChromaDB Contents

```powershell
ls f:\DoAnCN\fastapi_backend\chroma_db
# Expected: Directory exists with files
```

### Check PostgreSQL DocumentStorage

```powershell
cd f:\DoAnCN
python -c "import psycopg2; conn = psycopg2.connect('dbname=chatbotdb user=postgres password=yourpassword host=localhost'); cur = conn.cursor(); cur.execute('SELECT filename, upload_type, azure_url FROM documentstorage ORDER BY created_at DESC LIMIT 5;'); print(cur.fetchall())"
```

## Success Indicators ✅

1. **Frontend shows OCR results** ✅
2. **Backend logs show full pipeline** ✅
3. **ChromaDB has documents** ✅
4. **RAG query returns data** ✅
5. **Azure URL is accessible** ✅

## Failure Indicators ❌

1. **Frontend shows error message** ❌
2. **Backend logs show "connection refused"** ❌
3. **ChromaDB directory empty** ❌
4. **RAG query says "Chưa có dữ liệu"** ❌

## Common Issues & Fixes

### Issue: "Failed to fetch"

**Cause:** Backend not running
**Fix:** Start backend with `cd f:\DoAnCN\fastapi_backend && poetry run python main.py`

### Issue: "HTTP 500 Internal Server Error"

**Cause:** OCR or Azure error
**Fix:** Check backend terminal for detailed error, verify Tesseract and Azure credentials

### Issue: RAG query returns empty

**Cause:** Upload didn't reach RAG step
**Fix:**

1. Check `curl http://localhost:8000/chat/stats` - should show total_documents > 0
2. Check backend logs for "Processing document for RAG"
3. Verify ChromaDB directory exists: `ls f:\DoAnCN\fastapi_backend\chroma_db`

### Issue: Chatbot gives generic response

**Cause:** Pattern not matching or RAG not returning data
**Fix:**

1. Try exact query: "xem dữ liệu hóa đơn"
2. Check chatbot logs for "Matched intent: data_query"
3. Verify Google AI API key is valid

## Next Steps After Successful Test

1. ✅ Upload multiple invoices
2. ✅ Test different queries:
   - "cho tôi xem hóa đơn đã upload"
   - "tổng số hóa đơn là bao nhiêu"
   - "hóa đơn nào có giá trị cao nhất"
3. ✅ Verify Azure Storage has all files
4. ✅ Export RAG data for backup
5. ✅ Document API endpoints for team

## Ready to Test! 🚀

1. Make sure all 3 services are running
2. Open browser to http://localhost:5173
3. Press F12 to open console
4. Upload an invoice image
5. Watch the console and chat for results
6. Query for data: "xem dữ liệu hóa đơn"
7. Celebrate! 🎉
