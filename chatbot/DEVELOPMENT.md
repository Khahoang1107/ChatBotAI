# Chatbot Development Guide

## 🚀 Bắt đầu nhanh

1. **Cài đặt Python dependencies:**

   ```bash
   cd chatbot
   pip install -r requirements.txt
   ```

2. **Cấu hình environment:**

   ```bash
   cp .env.example .env
   # Chỉnh sửa .env với API keys của bạn
   ```

3. **Chạy chatbot service:**

   ```bash
   python app.py
   ```

4. **Test chatbot:**
   - Mở http://localhost:5000/health để kiểm tra health
   - Mở static/index.html trong browser để test UI

## 🏗️ Kiến trúc

```
chatbot/
├── app.py                 # Flask app chính
├── config.py             # Cấu hình chatbot
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── README.md            # Documentation
├── handlers/            # Xử lý logic chatbot
│   └── chat_handler.py  # Main chat logic
├── models/              # AI models và xử lý
│   └── ai_model.py      # OpenAI integration
├── utils/               # Utilities
│   ├── logger.py        # Logging setup
│   └── text_processor.py # Text processing
└── static/              # Frontend files
    └── index.html       # Chat UI
```

## 🔧 Cấu hình

### Environment Variables (.env)

```bash
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite:///chatbot.db
LOG_LEVEL=INFO
RATE_LIMIT_PER_MINUTE=30
```

### Config.py

- Bot name và description
- Model settings (GPT-3.5, temperature, max tokens)
- Response templates
- Intent patterns

## 🤖 Tính năng chính

### 1. Intent Detection

- Greeting: Chào hỏi
- Invoice Query: Câu hỏi về hóa đơn
- Help: Yêu cầu trợ giúp
- Goodbye: Tạm biệt

### 2. AI Response Generation

- OpenAI GPT integration
- Context-aware responses
- Fallback responses khi API fail

### 3. Text Processing

- Vietnamese text normalization
- Keyword extraction
- Entity extraction (số hóa đơn, ngày tháng, MST)

### 4. Conversation Management

- Session tracking
- Conversation history
- Context preservation

## 📚 API Endpoints

### POST /chat

Gửi tin nhắn đến chatbot

```json
{
  "message": "Tôi muốn tạo hóa đơn",
  "user_id": "user123"
}
```

Response:

```json
{
  "message": "Tôi có thể hỗ trợ bạn tạo hóa đơn...",
  "type": "text",
  "suggestions": ["Tạo hóa đơn mới", "Xem hướng dẫn"],
  "timestamp": "2025-01-15T10:30:00"
}
```

### GET /health

Kiểm tra trạng thái service

### GET /stats

Lấy thống kê chatbot

## 🎨 Frontend Integration

### Embed vào React

```jsx
// Tích hợp chatbot vào frontend React
const ChatBot = () => {
  const [messages, setMessages] = useState([]);

  const sendMessage = async (message) => {
    const response = await fetch('http://localhost:5000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, user_id: 'web_user' })
    });

    const data = await response.json();
    setMessages(prev => [...prev, data]);
  };

  return (
    // Chat UI components
  );
};
```

## 🔮 Tính năng nâng cao

### 1. Image Analysis

```python
# Phân tích ảnh hóa đơn
result = ai_model.analyze_invoice_image(image_path)
```

### 2. Voice Integration

- Speech-to-text
- Text-to-speech
- Voice commands

### 3. Document Search

- Vector database integration
- Semantic search
- Knowledge base queries

## 🚀 Triển khai

### Docker

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

### Production Settings

- Gunicorn WSGI server
- Redis for session storage
- PostgreSQL for persistent data
- Load balancing
- Rate limiting

## 📊 Monitoring

### Logging

- Structured logging with levels
- Request/response logging
- Error tracking
- Performance metrics

### Metrics

- Response time
- Success rate
- User satisfaction
- Popular queries

## 🔧 Development

### Adding New Intents

1. Update patterns in `chat_handler.py`
2. Add handler method
3. Update response templates
4. Test with sample inputs

### Improving AI Responses

1. Update system prompts in `ai_model.py`
2. Add domain-specific knowledge
3. Fine-tune temperature and max_tokens
4. Add fallback responses

### Testing

```bash
# Test API endpoints
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "user_id": "test"}'
```

## 🤝 Tích hợp với Frontend

Chatbot service chạy độc lập và có thể tích hợp với:

- React frontend qua REST API
- WebSocket cho real-time chat
- Webhook cho platform khác (Telegram, Facebook)

Để kết nối với frontend hiện tại:

1. Import chatbot component vào React app
2. Sử dụng API endpoints để giao tiếp
3. Style chatbot UI phù hợp với design system
