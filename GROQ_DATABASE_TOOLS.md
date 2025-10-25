# 🤖 Groq Database Tools Integration

## Giới thiệu

Groq AI giờ có thể **thao tác với database thông qua API tools** thay vì hardcode.

### Hai Workflow Song Song:

**Workflow 1: OCR Processing (xử lý ảnh hóa đơn)**

```
Upload ảnh → Enqueue → Worker xử lý → Tesseract OCR → Database
```

**Workflow 2: Chat với Groq (trả lời câu hỏi thông minh)**

```
User message → Groq analyze → Groq gọi API tools → Get data → Groq response
```

---

## 📋 Available Tools (Groq có thể gọi)

### 1. **get_all_invoices**

Lấy danh sách tất cả hóa đơn

```bash
curl -X POST http://localhost:8000/api/groq/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "get_all_invoices",
    "params": {
      "limit": 20
    }
  }'
```

### 2. **search_invoices**

Tìm kiếm hóa đơn theo keyword

```bash
curl -X POST http://localhost:8000/api/groq/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "search_invoices",
    "params": {
      "query": "công ty ABC",
      "limit": 10
    }
  }'
```

### 3. **get_invoice_by_id**

Lấy chi tiết một hóa đơn

```bash
curl -X POST http://localhost:8000/api/groq/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "get_invoice_by_id",
    "params": {
      "invoice_id": 1
    }
  }'
```

### 4. **get_statistics**

Lấy thống kê hóa đơn

```bash
curl -X GET http://localhost:8000/api/groq/tools/get_statistics
```

### 5. **filter_by_date**

Lọc hóa đơn theo khoảng thời gian

```bash
curl -X POST http://localhost:8000/api/groq/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "filter_by_date",
    "params": {
      "start_date": "2025-10-01",
      "end_date": "2025-10-31"
    }
  }'
```

### 6. **get_invoices_by_type**

Lấy hóa đơn theo loại

```bash
curl -X POST http://localhost:8000/api/groq/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "get_invoices_by_type",
    "params": {
      "invoice_type": "electricity"
    }
  }'
```

### 7. **get_high_value_invoices**

Lấy hóa đơn có giá trị cao

```bash
curl -X POST http://localhost:8000/api/groq/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "get_high_value_invoices",
    "params": {
      "min_amount": 5000000
    }
  }'
```

---

## 💬 Chat với Groq sử dụng Tools

### Endpoint: POST /chat/groq

Groq sẽ **tự động chọn tools** cần thiết để trả lời câu hỏi.

```bash
curl -X POST http://localhost:8000/chat/groq \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hóa đơn nào có tổng tiền cao nhất?",
    "user_id": "user1"
  }'
```

**Response:**

```json
{
  "message": "Hóa đơn có giá trị cao nhất là...",
  "type": "text",
  "method": "groq_with_tools",
  "iteration": 2,
  "timestamp": "2025-10-21T10:30:00"
}
```

### Ví dụ Các Câu Hỏi:

```bash
# Hỏi hóa đơn cao nhất
curl -X POST http://localhost:8000/chat/groq \
  -H "Content-Type: application/json" \
  -d '{"message": "Hóa đơn nào có tổng tiền cao nhất?", "user_id": "user1"}'

# Tìm kiếm hóa đơn
curl -X POST http://localhost:8000/chat/groq \
  -H "Content-Type: application/json" \
  -d '{"message": "Tìm hóa đơn của công ty ABC", "user_id": "user1"}'

# Lấy thống kê
curl -X POST http://localhost:8000/chat/groq \
  -H "Content-Type: application/json" \
  -d '{"message": "Cho tôi xem thống kê hóa đơn", "user_id": "user1"}'

# Hóa đơn tháng này
curl -X POST http://localhost:8000/chat/groq \
  -H "Content-Type: application/json" \
  -d '{"message": "Hóa đơn tháng 10 năm 2025", "user_id": "user1"}'
```

---

## 🧹 Simple Chat (không dùng Tools)

Endpoint: POST /chat/groq/simple

Dùng khi chỉ cần trả lời chung chung, không cần query database.

```bash
curl -X POST http://localhost:8000/chat/groq/simple \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Xin chào, bạn tên gì?",
    "user_id": "user1"
  }'
```

---

## 🔍 Xem Danh Sách Tools

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
      "parameters": {
        "type": "object",
        "properties": {
          "limit": {"type": "integer", "description": "Số hóa đơn tối đa"}
        }
      }
    },
    ...
  ]
}
```

---

## 🏗️ Architecture (2 Luồng Song Song)

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (port 8000)              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────┐     ┌───────────────────────┐     │
│  │   Chat Endpoints     │     │  OCR Endpoints        │     │
│  ├──────────────────────┤     ├───────────────────────┤     │
│  │                      │     │                       │     │
│  │ POST /chat           │     │ POST /upload-image    │     │
│  │ POST /chat/groq ⭐  │     │ (enqueue job)         │     │
│  │ POST /chat/simple    │     │ GET /api/ocr/job/id   │     │
│  │ POST /chat/groq/...  │     │                       │     │
│  └──────────────────────┘     └───────────────────────┘     │
│          │                              │                    │
│          ▼                              ▼                    │
│  ┌──────────────────────┐     ┌───────────────────────┐     │
│  │  Groq Chat Handler   │     │   OCR Enqueue         │     │
│  │ (with tools)         │     │ (job_id returned)     │     │
│  └──────────────────────┘     └───────────────────────┘     │
│          │                              │                    │
│          ▼                              ▼                    │
│  ┌──────────────────────┐     ┌───────────────────────┐     │
│  │ Groq Database Tools  │     │  PostgreSQL Queue     │     │
│  │ (7 tools available)  │     │ (ocr_jobs table)      │     │
│  └──────────────────────┘     └───────────────────────┘     │
│          │                              │                    │
│          ▼                              ▼                    │
│  ┌──────────────────────┐     ┌───────────────────────┐     │
│  │   PostgreSQL DB      │     │  Background Worker    │     │
│  │ (invoices table)     │     │ (polls every 5s)      │     │
│  └──────────────────────┘     └───────────────────────┘     │
│                                       │                     │
│                                       ▼                     │
│                            ┌───────────────────────┐        │
│                            │  Tesseract OCR        │        │
│                            │ (extract text)        │        │
│                            └───────────────────────┘        │
│                                       │                     │
│                                       ▼                     │
│                            ┌───────────────────────┐        │
│                            │  DB Update            │        │
│                            │ (save results)        │        │
│                            └───────────────────────┘        │
│                                                               │
└─────────────────────────────────────────────────────────────┘

⭐ = Groq tools integration (new)
```

---

## 📝 File Structure

```
backend/
├── main.py                        # FastAPI app + endpoints
├── groq_tools.py                 # ⭐ Groq database tools definitions
├── handlers/
│   ├── chat_handler.py           # Pattern-based chat
│   ├── hybrid_chat_handler.py    # Hybrid Rasa + AI
│   └── groq_chat_handler.py      # ⭐ Groq handler with tools
├── utils/
│   ├── database_tools.py         # Database queries
│   ├── database.py               # PostgreSQL connection
│   └── auth.py
└── worker.py                      # Background OCR processing
```

---

## 🚀 Flow Example

### User asks: "Hóa đơn nào có tổng tiền cao nhất?"

```
1. Frontend sends:
   POST /chat/groq
   {message: "Hóa đơn nào có tổng tiền cao nhất?"}

2. Backend receives request
   - Initializes Groq with tools description
   - Sends to Groq API

3. Groq analyzes:
   - Intent: "Find highest value invoice"
   - Best tool: "get_all_invoices" + "get_high_value_invoices"
   - Decides to call "get_high_value_invoices" with large threshold

4. Backend calls tool:
   GET /api/groq/tools/call
   {
     "tool_name": "get_high_value_invoices",
     "params": {"min_amount": 0}
   }

5. Tool returns invoices sorted by amount

6. Groq processes results:
   - Analyzes returned data
   - Formats human-readable response
   - Returns to user

7. Frontend displays:
   "Hóa đơn có giá trị cao nhất là..."
```

---

## 🧪 Testing

### 1. Test Groq Tools Directly

```bash
# Get all invoices
curl -X GET "http://localhost:8000/api/groq/tools/get_all_invoices?limit=5"

# Get statistics
curl -X GET "http://localhost:8000/api/groq/tools/get_statistics"
```

### 2. Test Groq Chat

```bash
# Chat with tools
curl -X POST http://localhost:8000/chat/groq \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Tìm 5 hóa đơn gần đây nhất",
    "user_id": "test_user"
  }'

# Simple chat
curl -X POST http://localhost:8000/chat/groq/simple \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hôm nay thời tiết thế nào?",
    "user_id": "test_user"
  }'
```

### 3. View API Docs

Open browser: http://localhost:8000/docs

---

## ⚙️ Configuration

### groq_tools.py

Định nghĩa các tools mà Groq có thể gọi:

```python
def get_tools_description(self) -> List[Dict[str, Any]]:
    """Trả về danh sách các tools mà Groq có thể gọi"""
    return [
        {
            "name": "get_all_invoices",
            "description": "Lấy danh sách tất cả hóa đơn",
            "parameters": { ... }
        },
        ...
    ]
```

### groq_chat_handler.py

Handler xử lý Groq chat với tools:

```python
async def _groq_with_tools(self, message: str, user_id: str,
                           tools_description: List[Dict]) -> Dict[str, Any]:
    """
    Groq analyze message + tự gọi tools nếu cần
    """
    while iteration < max_iterations:
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=tools_description,
            tool_choice="auto"  # Groq tự quyết định
        )

        if response.choices[0].finish_reason == "tool_calls":
            # Groq muốn gọi tools
            tool_calls = response.choices[0].message.tool_calls
            for tool_call in tool_calls:
                # Call tool
                tool_result = self.groq_tools.call_tool(...)
```

---

## 🔗 Integration with Frontend

### Option 1: Use /chat/groq endpoint (with tools)

```javascript
async function askGroq(message) {
  const response = await fetch("http://localhost:8000/chat/groq", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: message,
      user_id: "user123",
    }),
  });
  const data = await response.json();
  return data.message;
}

// Usage
const answer = await askGroq("Hóa đơn nào có giá trị cao nhất?");
console.log(answer);
```

### Option 2: Direct tool calls

```javascript
async function getInvoices(limit = 20) {
  const response = await fetch(
    `http://localhost:8000/api/groq/tools/get_all_invoices?limit=${limit}`
  );
  const data = await response.json();
  return data.result.invoices;
}
```

---

## 📊 Benefits

✅ **Thông minh**: Groq tự động chọn tools cần thiết  
✅ **Real-time**: Lấy dữ liệu mới nhất từ database  
✅ **Linh hoạt**: Dễ thêm tools mới  
✅ **Độc lập**: Không phụ thuộc vào hardcoded data  
✅ **Scalable**: Hỗ trợ nhiều người dùng đồng thời  
✅ **API-based**: Groq + Backend tách biệt, gọi qua HTTP

---

## 🐛 Troubleshooting

### Problem: "Groq tools not initialized"

**Solution**: Kiểm tra:

1. `.env` có `GROQ_API_KEY` không
2. `database_tools.py` có hoạt động không
3. Backend logs có lỗi gì không

```bash
# Check logs
tail -f backend.log
```

### Problem: "Tools not found"

**Solution**:

1. Xác nhận `groq_tools.py` có các methods
2. Kiểm tra tool names chính xác
3. Xem danh sách tools: GET /api/groq/tools

### Problem: "Tool call failed"

**Solution**:

1. Kiểm tra database connection
2. Xem database có dữ liệu không
3. Check parameters của tool call

---

## 📚 Next Steps

1. **Add more tools**: Tạo thêm tools trong `GroqDatabaseTools`
2. **Enhance responses**: Groq có thể format responses tốt hơn
3. **Add notifications**: WebSocket để real-time updates
4. **Analytics**: Track tool calls và chi tiêu API
