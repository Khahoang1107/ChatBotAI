# 🚀 Groq + Database Tools - Quick Start

## 2 Luồng Song Song Đã Hoạt Động ✅

```
┌─ Luồng 1: OCR Processing (xử lý ảnh) ─────────────┐
│  Upload ảnh → Enqueue job → Worker xử lý          │
│  → Tesseract OCR → Extract text → Save to DB      │
│  Endpoint: POST /upload-image                     │
│  Response time: 50-100ms                          │
└───────────────────────────────────────────────────┘

┌─ Luồng 2: Chat + Database Tools (Groq AI) ───────┐
│  User message → Groq analyze → Gọi API tools     │
│  → Get data from DB → Groq response              │
│  Endpoint: POST /chat/groq                       │
│  Response time: 2-3 giây (Groq API)              │
└───────────────────────────────────────────────────┘
```

---

## ✨ Groq Thao Tác Với Database

Groq **tự động gọi API tools** để lấy dữ liệu từ database mà không cần hardcode!

### 7 Tools Có Sẵn:

1. **get_all_invoices** - Lấy danh sách hóa đơn (limit)
2. **search_invoices** - Tìm kiếm theo keyword
3. **get_invoice_by_id** - Lấy chi tiết 1 hóa đơn
4. **get_statistics** - Lấy thống kê tổng quát
5. **filter_by_date** - Lọc theo khoảng ngày
6. **get_invoices_by_type** - Lọc theo loại (electricity, water, sale, service)
7. **get_high_value_invoices** - Lấy hóa đơn giá trị cao

---

## 💬 Test Chat with Groq

### Endpoint: `/chat/groq` (POST)

**Request:**

```bash
curl -X POST http://localhost:8000/chat/groq \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Có bao nhiêu hóa đơn?",
    "user_id": "user1"
  }'
```

**Response:**

```json
{
  "message": "Tôi đã nhận được kết quả từ tool get_all_invoices. Kết quả này cho thấy có tổng cộng 3 hóa đơn trong hệ thống...",
  "type": "text",
  "method": "groq_with_tools",
  "timestamp": "2025-10-21T10:45:00"
}
```

---

## 🧪 Test Examples

### 1. Hỏi số lượng hóa đơn

```bash
curl -X POST http://localhost:8000/chat/groq \
  -H "Content-Type: application/json" \
  -d '{"message":"Có bao nhiêu hóa đơn?", "user_id":"test"}'
```

### 2. Tìm kiếm hóa đơn

```bash
curl -X POST http://localhost:8000/chat/groq \
  -H "Content-Type: application/json" \
  -d '{"message":"Tìm hóa đơn của công ty ABC", "user_id":"test"}'
```

### 3. Thống kê

```bash
curl -X POST http://localhost:8000/chat/groq \
  -H "Content-Type: application/json" \
  -d '{"message":"Cho tôi xem thống kê hóa đơn", "user_id":"test"}'
```

### 4. Hóa đơn giá trị cao

```bash
curl -X POST http://localhost:8000/chat/groq \
  -H "Content-Type: application/json" \
  -d '{"message":"Hóa đơn nào có tổng tiền cao nhất?", "user_id":"test"}'
```

---

## 📋 Xem Danh Sách Tools

```bash
curl -X GET http://localhost:8000/api/groq/tools
```

**Response:**

```json
{
  "status": "success",
  "count": 7,
  "tools": [
    {
      "name": "get_all_invoices",
      "description": "Lấy danh sách tất cả hóa đơn từ database",
      "parameters": {...}
    },
    ...
  ]
}
```

---

## 🔧 Gọi Tools Trực Tiếp

### Cách 1: POST

```bash
curl -X POST http://localhost:8000/api/groq/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "get_all_invoices",
    "params": {"limit": 5}
  }'
```

### Cách 2: GET (cho tools đơn giản)

```bash
# Get all invoices with limit
curl -X GET "http://localhost:8000/api/groq/tools/get_all_invoices?limit=10"

# Get statistics
curl -X GET "http://localhost:8000/api/groq/tools/get_statistics"
```

---

## 🏗️ Architecture

### Files:

- **`backend/groq_tools.py`** - Define 7 tools
- **`backend/handlers/groq_chat_handler.py`** - Groq handler with tool calling
- **`backend/main.py`** - FastAPI endpoints
- **`.env`** - Contains GROQ_API_KEY

### Flow:

```
User Message
    ↓
POST /chat/groq
    ↓
GroqChatHandler.chat()
    ↓
Groq API (llama-3.3-70b-versatile)
    ↓
Groq analyzes → mentions tool name
    ↓
Backend detects tool → calls groq_tools.call_tool()
    ↓
Tool queries database
    ↓
Result returned to Groq (json.dumps with DecimalEncoder)
    ↓
Groq processes result → generates response
    ↓
Response returned to user
```

---

## 🐛 Fixed Issues

✅ **Decimal Serialization** - Database returns Decimal, JSON needs float

- Solution: Added `DecimalEncoder` class in both files

✅ **Groq Function Calling** - Groq API doesn't support native function calling like OpenAI

- Solution: Using prompt engineering + response parsing

✅ **Database Integration** - Groq tools now read from real database

- Solution: groq_tools.py methods query db_tools

---

## 📊 Two Parallel Workflows Summary

| Workflow    | Endpoint             | Purpose                | Response Time |
| ----------- | -------------------- | ---------------------- | ------------- |
| **OCR**     | `POST /upload-image` | Process invoice images | 50-100ms      |
| **Chat+DB** | `POST /chat/groq`    | Q&A with DB access     | 2-3s          |

Both can run **simultaneously without conflicts**! 🚀

---

## 🔐 Security Notes

⚠️ **Current Status**: Development mode

- GROQ_API_KEY in .env (should use secrets in production)
- No authentication on endpoints (add auth before production)
- Database connection local (secured by network in production)

---

## 📚 Next Steps

1. **Add more tools** - Create custom tools for specific queries
2. **Enhance Groq responses** - Better formatting, multi-language
3. **Add error handling** - Graceful fallbacks when tools fail
4. **Monitor performance** - Log tool calls, track latency
5. **Frontend integration** - Display tool results in UI
