# 🤖 Rasa-Chatbot Integration Guide

## Tổng Quan

Chatbot service đã được tích hợp với Rasa để cung cấp trải nghiệm chat thông minh hơn:

### **Architecture Flow:**
```
User Message → Chatbot Service → Rasa (Primary) → OpenAI (Fallback)
```

### **Ưu điểm:**
- ✅ **Rasa-first approach**: Sử dụng NLU mạnh mẽ của Rasa
- ✅ **Smart fallback**: Tự động chuyển sang OpenAI khi cần
- ✅ **Intent detection**: Nhận diện chính xác ý định người dùng
- ✅ **Entity extraction**: Trích xuất thông tin quan trọng
- ✅ **Vietnamese support**: Hỗ trợ tiếng Việt tốt

## 🚀 Cách Sử Dụng

### 1. Khởi động Services

```bash
# Khởi động tất cả services
docker-compose up -d

# Hoặc chỉ cần thiết
docker-compose up rasa chatbot backend postgres mongodb redis
```

### 2. Test Integration

**Linux/Mac:**
```bash
chmod +x test_rasa_chatbot.sh
./test_rasa_chatbot.sh
```

**Windows:**
```powershell
.\test_rasa_chatbot.ps1
```

### 3. API Usage

```bash
# Test chat với Rasa integration
curl -X POST http://localhost:5001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "xin chào, tôi cần giúp về hóa đơn",
    "user_id": "user123",
    "use_rasa_primary": true
  }'
```

## 🔧 Configuration

### Environment Variables

```yaml
# docker-compose.yml
environment:
  RASA_URL: http://rasa:5005  # Rasa service endpoint
  OPENAI_API_KEY: ${OPENAI_API_KEY:-}
```

### Handler Selection

```python
# chatbot/app.py
@app.route('/chat', methods=['POST'])
def chat():
    use_rasa_primary = data.get('use_rasa_primary', True)  # Rasa làm chính
    
    if use_rasa_primary:
        # Sử dụng Rasa làm engine chính
        response = rasa_chat.process_message(message, user_id)
    else:
        # Fallback to hybrid system
        response = hybrid_chat.process_message(message, user_id)
```

## 🎯 Response Flow

### 1. Rasa Response (Primary)
```json
{
  "message": "Xin chào! Tôi có thể giúp bạn tạo mẫu hóa đơn.",
  "method": "rasa",
  "intent": "ask_invoice_help",
  "confidence": 0.89,
  "entities": [],
  "suggestions": ["Tạo hóa đơn mới", "Xem mẫu có sẵn"]
}
```

### 2. OpenAI Fallback
```json
{
  "message": "Dựa trên ý định của bạn về hóa đơn, tôi có thể giúp...",
  "method": "openai_fallback", 
  "intent": "ask_invoice_help",
  "confidence": 0.45,
  "rasa_context": {...}
}
```

## 📊 Quality Checks

Chatbot sử dụng các tiêu chí để đánh giá chất lượng response từ Rasa:

### ✅ Good Rasa Response
- Confidence > 0.3
- Response length > 10 characters
- Không chứa generic patterns như "xin lỗi, tôi không hiểu"

### ❌ Poor Rasa Response → Fallback to OpenAI
- Confidence < 0.3
- Generic/default responses
- Empty responses
- Error responses

## 🔍 Monitoring & Debugging

### 1. Check Services Health

```bash
# Rasa health
curl http://localhost:5005/status

# Chatbot health
curl http://localhost:5001/health

# Both services
curl http://localhost:5001/health
```

### 2. View Logs

```bash
# Chatbot logs
docker-compose logs -f chatbot

# Rasa logs  
docker-compose logs -f rasa

# Both
docker-compose logs -f chatbot rasa
```

### 3. Debug Response Flow

Set log level to DEBUG in `chatbot/utils/logger.py`:

```python
logger.setLevel(logging.DEBUG)
```

## 🎨 Custom Intent Suggestions

Chatbot tự động tạo suggestions dựa trên intent:

```python
suggestion_map = {
    'greet': ['Tôi cần giúp về hóa đơn', 'Tạo mẫu hóa đơn'],
    'ask_invoice_help': ['Tạo hóa đơn mới', 'Xem mẫu có sẵn'],
    'create_invoice_template': ['Chọn loại mẫu', 'Thêm field'],
    # ... more intents
}
```

## 🚨 Troubleshooting

### Problem: Rasa Not Connecting
```bash
# Check Rasa service
docker-compose ps rasa
docker-compose logs rasa

# Restart Rasa
docker-compose restart rasa
```

### Problem: Always Fallback to OpenAI
- Train Rasa with more data: `cd rasa && rasa train`
- Check confidence threshold in `rasa_handler.py`
- Verify Rasa domain.yml and nlu.yml

### Problem: No OpenAI Fallback
- Check OPENAI_API_KEY environment variable
- Verify OpenAI API quotas
- Check network connectivity

## 📈 Performance Tips

1. **Train Rasa regularly** với data mới
2. **Monitor confidence scores** để tune thresholds
3. **Cache responses** cho queries phổ biến
4. **Use async processing** cho heavy workloads
5. **Monitor response times** của cả Rasa và OpenAI

## 🔄 Upgrade Path

### From Old Chatbot → Rasa Integrated:

1. **Backup existing data**
2. **Deploy new version** với Rasa integration
3. **Test thoroughly** với production data
4. **Monitor performance** trong vài ngày đầu
5. **Fine-tune thresholds** dựa trên feedback

---

## 🎉 Benefits

### Before (Pattern-based):
- ❌ Limited intent recognition
- ❌ No entity extraction  
- ❌ Hard-coded responses
- ❌ Poor Vietnamese support

### After (Rasa Integration):
- ✅ Advanced NLU with Rasa
- ✅ Entity extraction
- ✅ Smart fallback to OpenAI
- ✅ Better Vietnamese understanding
- ✅ Scalable conversation management
- ✅ Training data integration

**Result**: Smarter, more accurate, and more scalable chatbot! 🚀