# 🤖 Chat API Documentation

## 📡 **WebSocket Chat API**

### **WebSocket Connection**

```
ws://localhost:8000/chat/ws/{session_id}
```

**Ví dụ:**

```javascript
const ws = new WebSocket("ws://localhost:8000/chat/ws/test_session_123");
```

### **Message Format**

#### **Gửi tin nhắn text:**

```json
{
  "type": "text",
  "message": "Xin chào, tôi có thể hỏi gì về hóa đơn?"
}
```

#### **Nhận phản hồi từ bot:**

```json
{
  "type": "bot",
  "message": "Xin chào! Tôi có thể giúp bạn tìm hiểu thông tin từ các tài liệu đã upload.",
  "confidence": 0.8,
  "sources": 2,
  "timestamp": "2025-10-01T15:30:45.123Z"
}
```

## 📤 **HTTP API Endpoints**

### **1. Upload Image**

```http
POST /chat/upload-image/{session_id}
Content-Type: multipart/form-data
```

**Curl Example:**

```bash
curl -X POST \
  "http://localhost:8000/chat/upload-image/test_session_123" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@invoice.jpg"
```

**Response:**

```json
{
  "success": true,
  "azure_url": "https://storage.blob.core.windows.net/...",
  "message": "Image uploaded and processing started"
}
```

### **2. Chat Statistics**

```http
GET /chat/stats
```

**Response:**

```json
{
  "total_sessions": 15,
  "total_messages": 142,
  "total_documents": 8,
  "total_queries": 67,
  "active_connections": 3,
  "rag_stats": {
    "total_chunks": 234,
    "collection_name": "chat_documents",
    "embedding_model": "paraphrase-multilingual-MiniLM-L12-v2"
  }
}
```

### **3. Health Check**

```http
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2025-10-01T15:30:45.123456"
}
```

## 🧪 **Testing Guide**

### **1. Test WebSocket Chat**

#### **HTML Test Client:**

```html
<!DOCTYPE html>
<html>
  <head>
    <title>Chat Test</title>
  </head>
  <body>
    <div id="messages"></div>
    <input type="text" id="messageInput" placeholder="Nhập tin nhắn..." />
    <button onclick="sendMessage()">Gửi</button>

    <script>
      const ws = new WebSocket("ws://localhost:8000/chat/ws/test_session");
      const messages = document.getElementById("messages");

      ws.onmessage = function (event) {
        const data = JSON.parse(event.data);
        messages.innerHTML += `<p><strong>${data.type}:</strong> ${data.message}</p>`;
      };

      function sendMessage() {
        const input = document.getElementById("messageInput");
        ws.send(
          JSON.stringify({
            type: "text",
            message: input.value,
          })
        );
        input.value = "";
      }
    </script>
  </body>
</html>
```

### **2. Test with curl**

#### **Upload ảnh:**

```bash
# Upload invoice image
curl -X POST \
  "http://localhost:8000/chat/upload-image/test_session" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/invoice.jpg"
```

#### **Check stats:**

```bash
curl -X GET "http://localhost:8000/chat/stats"
```

#### **Health check:**

```bash
curl -X GET "http://localhost:8000/health"
```

### **3. Test với Python**

```python
import asyncio
import websockets
import json

async def test_chat():
    uri = "ws://localhost:8000/chat/ws/python_test"

    async with websockets.connect(uri) as websocket:
        # Send greeting
        await websocket.send(json.dumps({
            "type": "text",
            "message": "Xin chào!"
        }))

        # Wait for response
        response = await websocket.recv()
        print(f"Bot: {json.loads(response)}")

        # Send question
        await websocket.send(json.dumps({
            "type": "text",
            "message": "Tôi có thể hỏi gì về hóa đơn?"
        }))

        # Get response
        response = await websocket.recv()
        print(f"Bot: {json.loads(response)}")

# Run test
asyncio.run(test_chat())
```

## 🔧 **Environment Setup**

### **Required Environment Variables:**

```bash
# PostgreSQL
DATABASE_URL=postgresql://postgres:123@localhost:5432/chatbotdb

# Azure (Optional)
AZURE_STORAGE_CONNECTION_STRING=your_connection_string
AZURE_CV_ENDPOINT=https://your-cv-resource.cognitiveservices.azure.com/
AZURE_CV_KEY=your_computer_vision_key

# FastAPI
SECRET_KEY=your-secret-key
DEBUG=True
```

### **Start Backend:**

```bash
cd f:\DoAnCN\fastapi_backend
python main.py
```

## 📋 **Expected Workflows**

### **1. Basic Chat:**

1. Connect WebSocket → Receive welcome message
2. Send text query → Get AI response
3. Continue conversation

### **2. Image + Chat:**

1. Upload image via HTTP → OCR processing starts
2. WebSocket receives processing notification
3. Ask questions about uploaded image
4. Get RAG-based responses

### **3. Multi-session:**

1. Multiple users connect with different session_ids
2. Each session maintains separate conversation
3. Documents uploaded in one session available for that session's RAG

## 🚨 **Troubleshooting**

### **Common Issues:**

1. **WebSocket connection failed:**

   - Check if backend is running on port 8000
   - Verify session_id format

2. **No RAG responses:**

   - Check if documents were uploaded successfully
   - Verify embedding model is loaded

3. **Azure features not working:**
   - Ensure Azure credentials in .env
   - Check network connectivity

### **Debug Endpoints:**

- `GET /health` - Check if server is running
- `GET /chat/stats` - See system statistics
- WebSocket messages show real-time status

## 💡 **Tips**

- **Session IDs**: Sử dụng unique strings (UUID recommended)
- **File Types**: Chỉ support image files cho OCR
- **Message Size**: Không giới hạn length nhưng nên < 1000 characters
- **Concurrent Users**: Hỗ trợ multiple WebSocket connections

**🎯 Ready to test! Start backend và thử các endpoint trên.**
