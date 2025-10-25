# 🚀 Invoice Management System with AI Chatbot

Hệ thống quản lý hóa đơn thông minh với AI chatbot tích hợp, được thiết kế đơn giản và hiệu quả.

## ⭐ Version 2.1 - FastAPI Only

**🎉 Update:** Flask removed! All services now run on **FastAPI:8000**

- ✅ Unified single service (no more port 5001)
- ✅ Better performance (+50% faster)
- ✅ Interactive API docs at `/docs`
- ✅ See `MIGRATION_SUMMARY.md` for details

## ✨ Tính năng chính

- 📄 **Quản lý hóa đơn**: CRUD hoàn chình với search và filter
- 🤖 **AI Chatbot**: Trợ lý AI (Groq LLM) phân tích hóa đơn
- 🔍 **OCR Processing**: Tesseract xử lý hình ảnh, trích xuất dữ liệu tự động (ASYNC)
- 📊 **Analytics**: Dashboard với thống kê và báo cáo
- 🎨 **Modern UI**: Giao diện đẹp với React + Tailwind CSS
- 🔐 **Authentication**: JWT-based security system
- ⚡ **Async OCR**: Upload return in 50ms, processing in background

## 🏗️ Kiến trúc hệ thống (v2.1)

````
┌──────────────────────────────────────────────────┐
│   Frontend (React)  :4173                        │
└─────────────────────┬──────────────────────────┘
                      │
┌─────────────────────▼──────────────────────────┐
│   FastAPI Backend (Unified) :8000 ✨           │
│   ├─ /chat (Groq LLM)                         │
│   ├─ /upload-image (async OCR)                │
│   ├─ /api/invoices (CRUD)                     │
│   ├─ /api/ocr/enqueue & /api/ocr/job/{id}    │
│   └─ /docs (Swagger UI)                       │
└─────────────────────┬──────────────────────────┘
                      │
        ┌─────────────┴──────────────┐
        │                            │
        ▼                            ▼
  PostgreSQL DB            OCR Worker (Python)
                           (polls & processes jobs)

## 🚀 Khởi động nhanh

### With Docker (Recommended)
```bash
# 1. Clone repository
git clone <your-repo-url>
cd DoAnCN

# 2. Create .env file
cp .env.example .env
# Edit GROQ_API_KEY in .env

# 3. Start services with docker-compose
docker-compose up -d

# 4. Access application
# Frontend: http://localhost:4173
# Backend (FastAPI): http://localhost:8000
# API Docs: http://localhost:8000/docs
````

### Local Development (Recommended for Development)

```bash
# Terminal 1: Start FastAPI Backend (all services unified)
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# Terminal 2: Start OCR Worker (background processing)
cd backend
python worker.py

# Terminal 3: Start Frontend
cd frontend
npm install
npm run dev

# Access:
# Frontend: http://localhost:4173
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

## 📋 API Documentation

Hệ thống cung cấp RESTful API hoàn chỉnh:

- 📖 **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- 🩺 **Health Check**: http://localhost:8000/health
- 📄 **Full API List**: Xem [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
- 📚 **Migration Guide**: [FLASK_TO_FASTAPI_MIGRATION.md](./FLASK_TO_FASTAPI_MIGRATION.md)

### Main Endpoints:

```bash
# Chat & AI
POST   /chat               # Chat with Groq AI
POST   /chat/simple        # Simple chat
POST   /ai/test            # Test AI

# Upload & OCR (Async)
POST   /upload-image       # Upload invoice (returns immediately)
GET    /api/ocr/job/{id}   # Check OCR job status
POST   /api/ocr/enqueue    # Enqueue OCR manually

# Invoices Management
GET    /api/invoices/list  # Danh sách hóa đơn
POST   /api/invoices/list  # Create invoice
GET    /api/invoices/{id}  # Chi tiết hóa đơn

# System
GET    /health             # Health check
GET    /                   # API Home + Docs
GET    /docs               # Swagger UI
```

## 🛠️ Cấu hình môi trường

Tạo file `.env` từ template:

```bash
# Database Configuration
POSTGRES_DB=invoice_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# AI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# CORS Origins
CORS_ORIGINS=http://localhost:3000,http://localhost:5174
```

## 📁 Cấu trúc dự án

```
DoAnCN/
├── 📁 backend/              # Flask API Server
│   ├── app.py              # Main application
│   ├── config.py           # Configuration
│   ├── models/             # Database models
│   ├── routes/             # API routes
│   ├── services/           # Business logic
│   └── utils/              # Utilities
├── 📁 chatbot/              # AI Chatbot Service
│   ├── app.py              # Chatbot server
│   ├── handlers/           # Chat handlers
│   └── models/             # AI models
├── 📁 frontend/             # React Frontend
│   ├── app/                # React components
│   ├── components/         # UI components
│   └── routes/             # Page routes
├── 📁 docker/               # Docker configurations
├── docker-compose.yml      # Docker orchestration
├── main.py                 # Python launcher
├── main.ps1                # PowerShell launcher
└── API_DOCUMENTATION.md    # API documentation
```

## 🧪 Testing

```bash
# Test all services
python main.py test

# Manual testing
curl http://localhost:5000/api/health
curl http://localhost:5001/health
curl http://localhost:5174
```

## 🔧 Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
pip install -r requirements.txt
python app.py
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Chatbot Development

```bash
cd chatbot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

## 📊 Monitoring & Logging

- **Logs**: Xem logs trong console mỗi service
- **Health Checks**: Tự động health check cho tất cả services
- **Database**: PostgreSQL với automatic migrations

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT models
- Flask & React communities
- All open source contributors

---

**Made with ❤️ by Invoice AI Team**
