# Hệ thống MongoDB Training Data cho AI Chatbot

## Tổng quan

Hệ thống này được thiết kế để tự động lưu trữ và quản lý dữ liệu training cho AI chatbot mỗi khi có mẫu hóa đơn mới được tạo trong hệ thống. Chatbot sẽ học từ các mẫu này để cải thiện khả năng nhận dạng và xử lý hóa đơn.

## Kiến trúc hệ thống

### 1. Backend Components

#### Models
- **`training_data.py`**: MongoDB model để lưu trữ training data
- **`template.py`**: SQLAlchemy model cho invoice templates (đã có)

#### Services
- **`training_service.py`**: Service xử lý logic lưu trữ và truy xuất training data

#### Routes
- **`templates.py`**: Đã được cập nhật để tự động lưu training data khi CRUD templates
- **`ai_training.py`**: API endpoints mới cho chatbot truy vấn training data

### 2. Chatbot Components

#### Utils
- **`training_client.py`**: Client kết nối với backend API để lấy training data
- **`InvoicePatternMatcher`**: Class phân tích và extract thông tin từ text

#### Handlers
- **`chat_handler.py`**: Đã được tích hợp với training data để xử lý invoice analysis

## Cài đặt và Cấu hình

### 1. Cài đặt MongoDB Dependencies

```bash
# Backend dependencies
cd backend
pip install pymongo==4.8.0 motor==3.5.1

# Chatbot dependencies (requests đã có sẵn)
cd ../chatbot
pip install -r requirements.txt
```

### 2. Cấu hình MongoDB

#### Backend Config (`backend/config.py`)
```python
# MongoDB settings for AI training data
MONGODB_URL = os.environ.get('MONGODB_URL') or 'mongodb://localhost:27017/'
MONGODB_DB_NAME = os.environ.get('MONGODB_DB_NAME') or 'invoice_ai_training'
MONGODB_COLLECTION_TRAINING = 'invoice_training_data'
MONGODB_COLLECTION_PATTERNS = 'field_patterns'
```

#### Environment Variables
```bash
# .env file
MONGODB_URL=mongodb://localhost:27017/
MONGODB_DB_NAME=invoice_ai_training
```

### 3. Khởi động MongoDB

```bash
# Khởi động MongoDB local
mongod --dbpath /path/to/your/db

# Hoặc sử dụng Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

## Workflow tự động

### 1. Khi tạo Template mới

1. User tạo mẫu hóa đơn qua API `/api/templates`
2. Backend tự động:
   - Lưu template vào SQLite (như trước)
   - Extract fields từ template content
   - Tạo training record trong MongoDB
   - Log thông tin để theo dõi

### 2. Khi Chatbot xử lý tin nhắn

1. Chatbot nhận tin nhắn từ user
2. Tự động:
   - Lấy training data từ backend API
   - Áp dụng patterns đã học để extract thông tin
   - Trả về kết quả với độ tin cậy
   - Gợi ý loại template phù hợp

## API Endpoints

### Backend APIs cho Chatbot

#### 1. Lấy Training Data
```http
GET /api/ai-training/training-data
```

**Parameters:**
- `template_type` (optional): word, pdf, excel, html, xml
- `limit` (optional): số lượng records, default 100
- `include_patterns` (optional): có bao gồm field patterns, default true
- `include_statistics` (optional): có bao gồm thống kê, default false

**Response:**
```json
{
  "success": true,
  "data": {
    "templates": [...],
    "field_patterns": {...},
    "common_fields": [...]
  },
  "total_records": 150,
  "generated_at": "2024-01-01T10:00:00Z"
}
```

#### 2. Tìm Templates Tương Tự
```http
POST /api/ai-training/search-similar
```

**Body:**
```json
{
  "field_names": ["invoice_number", "company_name"],
  "limit": 20
}
```

#### 3. Lấy Field Patterns
```http
GET /api/ai-training/field-patterns
```

**Parameters:**
- `template_type` (optional): lọc theo loại template
- `field_name` (optional): lọc theo tên field cụ thể

#### 4. Thống kê Training Data
```http
GET /api/ai-training/statistics
```

#### 5. Health Check
```http
GET /api/ai-training/health
```

## Cách sử dụng Chatbot

### 1. Phân tích hóa đơn
```
User: "Phân tích hóa đơn số HD001 ngày 01/01/2024 của công ty ABC với tổng tiền 1,000,000 VND"

Bot: 🎯 **Thông tin hóa đơn đã nhận dạng:**

🟢 **Số hóa đơn**: HD001 (Độ tin cậy: 90%)
🟢 **Ngày hóa đơn**: 01/01/2024 (Độ tin cậy: 85%)
🟡 **Tên công ty**: ABC (Độ tin cậy: 60%)
🟢 **Tổng tiền**: 1,000,000 VND (Độ tin cậy: 95%)

💡 **Loại mẫu gợi ý**: PDF
📊 Dựa trên 150 mẫu hóa đơn đã học
```

### 2. Hỗ trợ về templates
```
User: "Cho tôi biết về các mẫu hóa đơn"

Bot: 📋 **Thống kê mẫu hóa đơn trong hệ thống:**

📊 **Tổng số mẫu**: 150

**Phân loại theo định dạng:**
• **PDF**: 80 mẫu (TB 12 trường thông tin)
• **WORD**: 45 mẫu (TB 10 trường thông tin)
• **EXCEL**: 25 mẫu (TB 15 trường thông tin)

**🏷️ Trường thông tin phổ biến:**
• Số hóa đơn
• Ngày hóa đơn
• Tên công ty
• Mã số thuế
• Tổng tiền
```

## Monitoring và Debugging

### 1. Kiểm tra kết nối MongoDB
```python
from services.training_service import TrainingDataService

service = TrainingDataService()
if service.training_data:
    print("MongoDB connected successfully")
    stats = service.get_training_statistics()
    print(f"Total training records: {stats.get('total_records', 0)}")
else:
    print("MongoDB connection failed")
```

### 2. Kiểm tra Chatbot connection
```python
from utils.training_client import TrainingDataClient

client = TrainingDataClient()
health = client.check_health()
print(f"Backend health: {'OK' if health else 'ERROR'}")
```

### 3. Logs để theo dõi

Backend logs:
- Template creation + training data save
- API calls từ chatbot
- MongoDB connection status

Chatbot logs:
- Training data fetch requests
- Pattern matching results
- API connection health

## Cấu trúc dữ liệu MongoDB

### Collection: invoice_training_data

```json
{
  "_id": "ObjectId",
  "template_id": "string",
  "template_name": "string", 
  "template_type": "word|pdf|excel|html|xml",
  "template_content": "string",
  "fields": [
    {
      "field_name": "string",
      "field_type": "string",
      "data_type": "string",
      "is_required": "boolean",
      "pattern": "string"
    }
  ],
  "field_patterns": {
    "extraction_patterns": {...},
    "validation_patterns": {...},
    "field_relationships": [...],
    "content_structure": {...}
  },
  "metadata": {...},
  "created_at": "datetime",
  "updated_at": "datetime",
  "version": "number",
  "is_validated": "boolean",
  "training_score": "number",
  "usage_count": "number"
}
```

## Tính năng nâng cao

### 1. Auto-learning
- Mỗi khi user tạo template mới, hệ thống tự động học
- Patterns được cập nhật real-time
- Chatbot cache patterns để tăng tốc

### 2. Field Recognition
- Nhận dạng tự động các trường phổ biến
- Gợi ý template type dựa trên fields
- Validation patterns cho từng loại field

### 3. Statistics & Analytics
- Thống kê usage theo template type
- Phân tích độ chính xác của patterns
- Monitoring training data quality

## Troubleshooting

### Vấn đề thường gặp:

1. **MongoDB không kết nối được**
   - Kiểm tra MongoDB service đang chạy
   - Verify connection string trong config
   - Check firewall/network settings

2. **Chatbot không nhận được training data**
   - Kiểm tra backend API đang chạy
   - Verify health endpoint: `/api/ai-training/health`
   - Check logs cho request/response

3. **Pattern matching không chính xác**
   - Refresh training patterns: `refresh_training_data()`
   - Kiểm tra quality của training data
   - Validate patterns trong MongoDB

4. **Performance chậm**
   - Tăng cache timeout cho training client
   - Optimize MongoDB queries
   - Giảm limit khi fetch training data

## Tương lai phát triển

1. **Machine Learning Integration**
   - Sử dụng ML models để improve pattern recognition
   - Auto-scoring training data quality
   - Predictive field extraction

2. **Advanced Analytics**
   - Dashboard cho training data insights
   - A/B testing cho pattern improvements
   - User feedback integration

3. **Scale & Performance**
   - MongoDB clustering
   - Redis caching layer
   - Background processing cho training data

## Kết luận

Hệ thống này tạo ra một vòng lặp học tập tự động:
- User tạo templates → Hệ thống học patterns
- Chatbot sử dụng patterns → Cải thiện trải nghiệm user
- User tạo thêm templates → Patterns càng chính xác

Điều này giúp chatbot ngày càng thông minh trong việc xử lý và hiểu các loại hóa đơn khác nhau.