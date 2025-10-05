# Frontend Upload Flow - FIXED ✅

## Problem Summary

Previously, the frontend `ChatBot.tsx` was sending **raw File objects** to the chatbot instead of processing them through the backend OCR pipeline. This meant:

- ❌ No OCR extraction
- ❌ No Azure Storage upload
- ❌ No RAG database storage
- ❌ No data available for queries

## Solution Implemented

### Modified File: `frontend/app/components/ChatBot.tsx`

**Function Changed:** `processFiles()`

**Previous Behavior:**

```typescript
const processFiles = (files: File[]) => {
  // Created file previews
  // Simulated processing with setTimeout
  // Never called backend OCR API ❌
};
```

**New Behavior:**

```typescript
const processFiles = async (files: File[]) => {
  // 1. Create file previews (same as before)
  // 2. Upload each file to backend OCR endpoint ✅
  // 3. Wait for OCR + Azure + RAG processing ✅
  // 4. Display OCR results to user ✅
  // 5. Handle errors gracefully ✅
};
```

### Complete Upload Flow (After Fix)

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER UPLOADS IMAGE                          │
│                 (via camera or file picker)                     │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  Frontend: processFiles() in ChatBot.tsx                        │
│  - Creates file preview                                          │
│  - Shows "Đang xử lý OCR và lưu vào hệ thống..."               │
│  - Calls: POST http://localhost:8000/api/ocr/camera-ocr         │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  Backend: /api/ocr/camera-ocr endpoint (main.py line 51-60)     │
│  - Generates session_id from file hash                          │
│  - Redirects to upload_chat_image()                             │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  Backend: upload_chat_image() (websocket_chat.py line 286-404)  │
│                                                                  │
│  Step 1: OCR Extraction                                         │
│  - Tesseract extracts text from image                           │
│  - Extracts structured fields (Invoice #, Date, Total, etc.)    │
│                                                                  │
│  Step 2: Azure Storage Upload (line 327-336)                    │
│  - Uploads image to Azure Blob Storage                          │
│  - Returns permanent azure_url                                  │
│                                                                  │
│  Step 3: PostgreSQL Storage (line 339-350)                      │
│  - Saves to DocumentStorage table:                              │
│    * azure_url                                                  │
│    * ocr_results (JSON with extracted_text, fields)             │
│    * extracted_data (JSON structured data)                      │
│    * session_id, filename, upload_type                          │
│                                                                  │
│  Step 4: RAG Processing (line 362-369)                          │
│  - Chunks extracted text                                        │
│  - Generates embeddings with sentence-transformers             │
│  - Stores in ChromaDB vector database                           │
│                                                                  │
│  Returns JSON:                                                  │
│  {                                                              │
│    "session_id": "...",                                         │
│    "ocr_results": {...},                                        │
│    "azure_url": "https://...",                                  │
│    "rag_processed": true                                        │
│  }                                                              │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  Frontend: processFiles() receives response                     │
│  - Updates file status to 'processed'                           │
│  - Displays OCR results:                                        │
│    ✅ Đã xử lý xong: filename                                   │
│    📝 Kết quả OCR: [extracted text]                             │
│    💾 Đã lưu vào hệ thống RAG và Azure Storage                 │
│    🔗 URL: [azure_url]                                          │
└─────────────────────────────────────────────────────────────────┘

Now when user asks: "xem dữ liệu hóa đơn" or "cho tôi xem hóa đơn đã upload"
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  Chatbot: handle_data_query() in chat_handler.py               │
│  - Calls: POST http://localhost:8000/chat/rag-search            │
│  - Query: "xem dữ liệu hóa đơn"                                 │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  Backend: /chat/rag-search endpoint                             │
│  - Embeds query with sentence-transformers                      │
│  - Searches ChromaDB for similar documents                      │
│  - Returns top 5 matching documents with:                       │
│    * document_id                                                │
│    * content (extracted text)                                   │
│    * metadata (filename, azure_url, date)                       │
│    * distance (similarity score)                                │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  Chatbot: handle_data_query() builds RAG context               │
│  - Formats top 5 documents into context string                  │
│  - Creates prompt:                                              │
│    "THÔNG TIN TỪ HỆ THỐNG:\n[RAG context]\nCÂU HỎI: [query]"  │
│  - Calls Google Gemini AI: generate_response(prompt)           │
│  - Returns intelligent, context-aware answer ✅                 │
└─────────────────────────────────────────────────────────────────┘
```

## Code Changes Made

### ChatBot.tsx Line 379 (processFiles function)

**Changed from:**

```typescript
// Simulate file processing
newFiles.forEach((uploadedFile) => {
  setTimeout(() => {
    setUploadedFiles((prev) =>
      prev.map((f) =>
        f.id === uploadedFile.id ? { ...f, status: "processed" } : f
      )
    );
  }, 2000);
});
```

**Changed to:**

```typescript
// Gửi từng file đến backend để xử lý OCR + Azure + RAG
for (const uploadedFile of newFiles) {
  try {
    const formData = new FormData();
    formData.append("file", uploadedFile.file);

    // Gọi backend OCR endpoint
    const response = await fetch("http://localhost:8000/api/ocr/camera-ocr", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();

    // Cập nhật trạng thái file thành công
    setUploadedFiles((prev) =>
      prev.map((f) =>
        f.id === uploadedFile.id ? { ...f, status: "processed" } : f
      )
    );

    // Hiển thị kết quả OCR
    const ocrMessage =
      `✅ Đã xử lý xong: ${uploadedFile.file.name}\n\n` +
      `📝 Kết quả OCR:\n${
        result.ocr_results?.extracted_text || "Không trích xuất được văn bản"
      }\n\n` +
      `💾 Đã lưu vào hệ thống RAG và Azure Storage\n` +
      `🔗 URL: ${result.azure_url || "N/A"}`;

    setMessages((prev) => [
      ...prev,
      {
        id: Date.now().toString(),
        type: "bot",
        content: ocrMessage,
        timestamp: new Date(),
      },
    ]);
  } catch (error) {
    console.error("Error processing file:", uploadedFile.file.name, error);

    // Hiển thị thông báo lỗi
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now().toString(),
        type: "bot",
        content: `❌ Lỗi khi xử lý file: ${uploadedFile.file.name}\n${
          error instanceof Error ? error.message : "Unknown error"
        }`,
        timestamp: new Date(),
      },
    ]);
  }
}
```

## Testing Instructions

### 1. Start All Services

```powershell
# Terminal 1: Start Backend
cd f:\DoAnCN\fastapi_backend
poetry run python main.py

# Terminal 2: Start Chatbot
cd f:\DoAnCN\chatbot
python app.py

# Terminal 3: Start Frontend
cd f:\DoAnCN\frontend
npm run dev
```

### 2. Test Upload Flow

1. **Open frontend:** http://localhost:5173 or http://localhost:5174
2. **Click camera icon** or **upload file button**
3. **Upload an invoice image**
4. **Expected behavior:**
   - ✅ Shows "Đang xử lý OCR và lưu vào hệ thống..."
   - ✅ After processing, shows:
     - "✅ Đã xử lý xong: [filename]"
     - "📝 Kết quả OCR: [extracted text]"
     - "💾 Đã lưu vào hệ thống RAG và Azure Storage"
     - "🔗 URL: [azure_url]"

### 3. Test RAG Query

1. **Type in chat:** "xem dữ liệu hóa đơn" or "cho tôi xem hóa đơn đã upload"
2. **Expected behavior:**
   - ✅ Returns intelligent response with invoice data
   - ✅ Uses Google Gemini AI to format response
   - ✅ Includes information from uploaded invoice

### 4. Verify Backend Logs

Check backend terminal for logs:

```
📤 Chat upload: [filename]
Processing document for RAG: [doc_id]
Added 3 chunks to RAG database
RAG stats: {'total_documents': 1, ...}
```

### 5. Manual API Test (Optional)

```powershell
# Test upload endpoint directly
curl.exe -X POST `
  -F "file=@path\to\image.jpg" `
  http://localhost:8000/api/ocr/camera-ocr

# Check RAG stats
curl http://localhost:8000/chat/stats

# Test RAG search
curl.exe -X POST `
  -H "Content-Type: application/json" `
  -d '{"query":"hóa đơn","top_k":5}' `
  http://localhost:8000/chat/rag-search
```

## Verification Checklist

- [x] ✅ Frontend modified: `processFiles()` now calls backend OCR API
- [x] ✅ Backend endpoint exists: `/api/ocr/camera-ocr` (main.py line 51-60)
- [x] ✅ Full pipeline implemented: OCR → Azure → PostgreSQL → RAG
- [x] ✅ Error handling added to frontend
- [x] ✅ OCR results displayed to user
- [ ] ⏳ **NEXT: Test with real image upload**
- [ ] ⏳ **NEXT: Verify ChromaDB receives documents**
- [ ] ⏳ **NEXT: Test RAG query returns data**

## Expected Results After Fix

1. **Upload image** → Backend processes → Displays OCR results
2. **ChromaDB** → Should have documents (check `f:\DoAnCN\fastapi_backend\chroma_db`)
3. **Azure Storage** → Should have blob with URL
4. **PostgreSQL** → Should have DocumentStorage record
5. **Query "xem dữ liệu"** → Returns intelligent response with invoice data

## Troubleshooting

### If upload fails:

1. Check backend terminal for errors
2. Verify Tesseract is installed: `tesseract --version`
3. Check Azure credentials in `.env`
4. Check PostgreSQL connection

### If RAG query returns "Chưa có dữ liệu":

1. Check ChromaDB directory: `ls f:\DoAnCN\fastapi_backend\chroma_db`
2. Check RAG stats: `curl http://localhost:8000/chat/stats`
3. Verify upload reached RAG step (check backend logs)

### If frontend shows error:

1. Check browser console (F12)
2. Verify backend is running: `curl http://localhost:8000/health`
3. Check CORS settings in backend
