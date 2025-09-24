# Hybrid Chat System

Hệ thống chat hybrid kết hợp Rasa và Chatbot để cung cấp trải nghiệm chat tốt nhất.

## Tổng quan

Hybrid Chat System hoạt động theo mô hình fallback:

1. **Rasa First**: Tin nhắn được gửi tới Rasa trước
2. **Quality Check**: Kiểm tra chất lượng response từ Rasa
3. **Chatbot Fallback**: Nếu Rasa không đáp ứng, chuyển sang Chatbot
4. **Best Response**: Trả về response tốt nhất

## Kiến trúc

```
Frontend → Backend API → Hybrid Service → Rasa/Chatbot
```

### Components:

- **Frontend**: React component (`HybridChatInterface.tsx`)
- **Backend**: Flask API (`/api/hybrid-chat/*`)
- **Hybrid Service**: Logic xử lý fallback (`hybrid_chat_service.py`)
- **Rasa**: NLU và Dialog Management
- **Chatbot**: AI-powered chatbot với OpenAI

## API Endpoints

### 1. Chat với Authentication

```
POST /api/hybrid-chat/chat
Headers: Authorization: Bearer <token>
Body: {
  "message": "Tin nhắn của user",
  "conversation_id": "optional"
}
```

### 2. Chat Anonymous

```
POST /api/hybrid-chat/chat/anonymous
Body: {
  "message": "Tin nhắn của user",
  "session_id": "optional"
}
```

### 3. Health Check

```
GET /api/hybrid-chat/health
```

### 4. Configuration

```
GET /api/hybrid-chat/config
```

## Response Format

```json
{
  "success": true,
  "data": {
    "message": "Tin nhắn gốc",
    "response": "Phản hồi từ system",
    "source": "rasa|chatbot|fallback|error",
    "confidence": 0.8,
    "timestamp": "2025-09-23T10:30:00Z",
    "user_id": "user123"
  }
}
```

## Cấu hình

### Environment Variables

Trong `docker-compose.yml`:

```yaml
services:
  backend:
    environment:
      - RASA_URL=http://rasa:5005
      - CHATBOT_URL=http://chatbot:5001

  rasa:
    ports:
      - "5005:5005"

  chatbot:
    ports:
      - "5001:5001"
```

### Hybrid Service Settings

Trong `hybrid_chat_service.py`:

```python
self.confidence_threshold = 0.7  # Ngưỡng confidence cho Rasa
self.request_timeout = 10        # Timeout cho requests
```

## Cách sử dụng

### 1. Khởi động services

```bash
# Khởi động tất cả services
docker-compose up -d

# Hoặc chỉ cần thiết
docker-compose up backend rasa chatbot postgres mongodb redis
```

### 2. Test hệ thống

```bash
# Chạy test script
chmod +x test_hybrid_system.sh
./test_hybrid_system.sh

# Hoặc test thủ công
curl http://localhost:5000/api/hybrid-chat/health
```

### 3. Sử dụng trong Frontend

```tsx
import { HybridChatInterface } from "./components/HybridChatInterface";

function App() {
  return (
    <div>
      <HybridChatInterface />
    </div>
  );
}
```

## Troubleshooting

### 1. Rasa không hoạt động

```bash
# Kiểm tra Rasa status
curl http://localhost:5005/status

# Xem logs
docker logs invoice_rasa

# Restart Rasa
docker restart invoice_rasa
```

### 2. Chatbot không hoạt động

```bash
# Kiểm tra Chatbot health
curl http://localhost:5001/health

# Xem logs
docker logs invoice_chatbot

# Test direct
curl -X POST http://localhost:5001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "user_id": "test"}'
```

### 3. Backend không kết nối được

```bash
# Kiểm tra network
docker network ls
docker network inspect doan-cn_invoice_network

# Kiểm tra service discovery
docker exec invoice_backend ping rasa
docker exec invoice_backend ping chatbot
```

### 4. Frontend không gọi được API

- Kiểm tra CORS settings trong `app.py`
- Kiểm tra JWT token nếu dùng authenticated endpoints
- Kiểm tra network trong browser DevTools

## Monitoring

### Health Check Dashboard

Truy cập `/api/hybrid-chat/health` để xem:

- Status của Rasa
- Status của Chatbot
- Response time của các services
- Overall system health

### Logs

```bash
# Backend logs
docker logs invoice_backend

# Rasa logs
docker logs invoice_rasa

# Chatbot logs
docker logs invoice_chatbot
```

## Tùy chỉnh

### 1. Thay đổi Logic Fallback

Trong `hybrid_chat_service.py`, method `_is_good_response()`:

```python
def _is_good_response(self, rasa_response: Dict[str, Any]) -> bool:
    # Tùy chỉnh logic kiểm tra chất lượng response
    confidence = rasa_response.get("confidence", 0.0)
    if confidence < self.confidence_threshold:
        return False
    # Thêm logic khác...
    return True
```

### 2. Thêm Service khác

Mở rộng `HybridChatService` để hỗ trợ nhiều backend:

```python
def _try_service_3(self, message: str, user_id: str):
    # Logic cho service thứ 3
    pass
```

### 3. Custom Response Processing

```python
def _process_response(self, response, source):
    # Xử lý response trước khi trả về
    return processed_response
```

## Best Practices

1. **Error Handling**: Luôn có fallback cho mọi failure case
2. **Timeout**: Set timeout hợp lý để không block user
3. **Monitoring**: Monitor response time và success rate
4. **Caching**: Cache responses để improve performance
5. **Logging**: Log đầy đủ để debug

## Development

### Local Development

```bash
# Chạy chỉ backend services
docker-compose up postgres mongodb redis rasa chatbot

# Chạy backend local
cd backend
python app.py

# Test
curl http://localhost:5000/api/hybrid-chat/health
```

### Adding Features

1. Tạo method mới trong `HybridChatService`
2. Thêm endpoint trong `hybrid_chat.py`
3. Update frontend component nếu cần
4. Thêm tests

## Performance

### Metrics to Monitor

- Response time của mỗi service
- Success rate của Rasa vs Chatbot
- Overall system latency
- Error rates

### Optimization

- Connection pooling cho requests
- Caching responses
- Async processing
- Load balancing multiple instances
