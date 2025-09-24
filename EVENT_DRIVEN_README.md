# 🚀 Event-Driven OCR Processing Guide

## 📋 Tổng quan

Hệ thống OCR Event-Driven cho phép xử lý hình ảnh hóa đơn bất đồng bộ, không bắt người dùng chờ đợi. Thay vì xử lý đồng bộ mất 30-60 giây, user sẽ nhận response ngay lập tức và được thông báo khi xử lý hoàn tất.

## 🏗️ Kiến trúc Event-Driven

```
📱 Frontend Upload → 📡 API Endpoint → ⚡ Queue Task → 🔄 Background Processing → 📲 Real-time Notification
```

### Thành phần chính:

1. **Redis**: Message broker cho task queue
2. **Celery**: Background task processor
3. **WebSocket**: Real-time notifications
4. **PostgreSQL**: Lưu trữ kết quả OCR

## 🚀 API Endpoints

### 1. Async OCR Processing

```http
POST /api/ocr-async/process-async
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data

{
  "file": <image_file>,
  "template_id": 123,              // Optional
  "confidence_threshold": 0.7,     // Optional
  "priority": "normal"             // low|normal|high
}
```

**Response (202 Accepted):**

```json
{
  "message": "✅ File uploaded successfully! OCR processing started in background.",
  "ocr_result_id": 456,
  "task_id": "abc-123-def",
  "status": "queued",
  "estimated_time": "30-60 seconds",
  "check_status_url": "/api/ocr-async/status/456",
  "notification": "You will be notified when processing completes"
}
```

### 2. Check Processing Status

```http
GET /api/ocr-async/status/456
Authorization: Bearer <jwt_token>
```

**Response:**

```json
{
  "ocr_result_id": 456,
  "status": "processing", // queued|processing|completed|failed
  "task_id": "abc-123-def",
  "task_status": "PROCESSING",
  "task_info": {
    "message": "Processing image with OCR...",
    "progress": 40
  }
}
```

**When completed:**

```json
{
  "ocr_result_id": 456,
  "status": "completed",
  "confidence_score": 0.92,
  "processing_time": 35.2,
  "extracted_text": "...",
  "extracted_data": {
    "invoice_number": "INV-2024-001",
    "total_amount": 1500000,
    "date": "2024-01-15"
  }
}
```

### 3. Bulk OCR Processing

```http
POST /api/ocr-async/process-bulk
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data

{
  "files": [<file1>, <file2>, <file3>],
  "template_id": 123,
  "confidence_threshold": 0.7
}
```

### 4. Cancel Task

```http
POST /api/ocr-async/cancel/abc-123-def
Authorization: Bearer <jwt_token>
```

### 5. Queue Statistics

```http
GET /api/ocr-async/queue-stats
Authorization: Bearer <jwt_token>
```

## 📡 Real-time Notifications

### WebSocket Connection

```javascript
import io from "socket.io-client";

const socket = io("http://localhost:5000");

// Connect and join user notifications
socket.on("connect", () => {
  socket.emit("join_notifications", { user_id: "user_123" });
});

// Listen for OCR completion notifications
socket.on("notification", (data) => {
  if (data.type === "ocr_completed") {
    console.log("✅ OCR completed!", data);
    // Update UI with results
    displayOCRResults(data.data.ocr_result_id);
  } else if (data.type === "ocr_failed") {
    console.log("❌ OCR failed:", data.message);
    // Show error to user
    showError(data.data.error_message);
  }
});
```

### Notification Types

- `ocr_completed`: OCR processing hoàn tất thành công
- `ocr_failed`: OCR processing thất bại
- `ai_training`: AI model training updates
- `system`: System-wide notifications

## 🐳 Docker Services

### Chạy đầy đủ hệ thống Event-Driven:

```bash
# Chạy tất cả services bao gồm Celery worker
docker-compose up -d

# Hoặc chỉ chạy core services
docker-compose up -d mongodb postgres redis backend frontend celery_worker
```

### Chạy với monitoring (optional):

```bash
# Bao gồm Celery Flower để monitor tasks
docker-compose --profile monitoring up -d

# Truy cập Flower UI: http://localhost:5555
```

### Chạy với scheduled tasks (optional):

```bash
# Bao gồm Celery Beat cho scheduled tasks
docker-compose --profile celery-beat up -d
```

## 🔧 Configuration

### Environment Variables

```env
# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Celery Configuration
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Database
DATABASE_URL=postgresql://user:pass@postgres:5432/db

# OCR Settings
OCR_CONFIDENCE_THRESHOLD=0.7
OCR_MAX_FILE_SIZE=10MB
OCR_SUPPORTED_FORMATS=jpg,png,pdf,tiff
```

### Celery Queues

- `ocr_queue`: OCR processing tasks (high CPU)
- `ai_queue`: AI training tasks (high memory)
- `notification_queue`: Notification tasks (low priority)
- `default`: General background tasks

## 📊 Monitoring

### 1. Celery Flower (Web UI)

```bash
# Access: http://localhost:5555
docker-compose --profile monitoring up -d celery_flower
```

### 2. Queue Stats API

```http
GET /api/ocr-async/queue-stats
```

### 3. Task Status Tracking

```http
GET /api/ocr-async/status/{ocr_result_id}
```

## 🧪 Testing Event-Driven Flow

### 1. Upload test file:

```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@test_invoice.jpg" \
  -F "priority=high" \
  http://localhost:5000/api/ocr-async/process-async
```

### 2. Check status:

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:5000/api/ocr-async/status/456
```

### 3. Monitor via WebSocket:

```javascript
const socket = io("http://localhost:5000");
socket.emit("join_notifications", { user_id: "test_user" });
socket.on("notification", console.log);
```

## ✅ Lợi ích Event-Driven

1. **🚀 Response Time**: User nhận phản hồi ngay (<100ms)
2. **⚡ Scalability**: Xử lý nhiều files đồng thời
3. **🔄 Reliability**: Retry mechanism cho failed tasks
4. **📊 Monitoring**: Real-time queue statistics
5. **🔔 User Experience**: Real-time notifications
6. **⚖️ Load Balancing**: Distribute tasks across workers

## 🚨 Error Handling

### Retry Logic

- **Temporary failures**: Auto retry 3 times with exponential backoff
- **Permanent failures**: Mark as failed and notify user
- **Network issues**: Queue task for later processing

### Graceful Degradation

- If Celery worker down → Fallback to synchronous processing
- If Redis down → Store tasks in database queue
- If notification fails → Log error but continue processing

## 📈 Performance Tuning

### Celery Worker Configuration

```bash
# High throughput
celery -A celery_config.celery worker --concurrency=8 --pool=prefork

# Memory optimization
celery -A celery_config.celery worker --concurrency=4 --max-memory-per-child=200000

# CPU optimization
celery -A celery_config.celery worker --concurrency=2 --pool=solo
```

### Redis Optimization

```conf
# redis.conf
maxmemory 512mb
maxmemory-policy allkeys-lru
save 60 1000
```

## 🔐 Security

- **Authentication**: JWT tokens required for all endpoints
- **File validation**: Strict file type and size limits
- **Rate limiting**: Prevent queue flooding
- **Input sanitization**: Secure file handling

---

🎉 **Kết quả**: Thay vì user phải chờ 30-60 giây, giờ họ upload file và nhận response ngay lập tức, sau đó được thông báo real-time khi OCR hoàn tất!
