# 🚀 Invoice Management System with AI Chatbot

Hệ thống quản lý hóa đơn thông minh với AI chatbot tích hợp, được thiết kế đơn giản và hiệu quả.

## ✨ Tính năng chính

- 📄 **Quản lý hóa đơn**: CRUD hoàn chình với search và filter
- 🤖 **AI Chatbot**: Trợ lý AI giúp phân tích hóa đơn và trả lời câu hỏi
- 🔍 **OCR Processing**: Xử lý hình ảnh và trích xuất dữ liệu tự động
- 📊 **Analytics**: Dashboard với thống kê và báo cáo
- 🎨 **Modern UI**: Giao diện đẹp với React + Tailwind CSS
- 🔐 **Authentication**: JWT-based security system

## 🏗️ Kiến trúc hệ thống

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Chatbot       │
│   (React)       │◄──►│   (Flask)       │◄──►│   (Flask)       │
│   Port: 5174    │    │   Port: 5000    │    │   Port: 5001    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    │   Port: 5432    │
                    └─────────────────┘
```

## 🚀 Khởi động nhanh

### Với Docker (Khuyến nghị)
```bash
# 1. Clone repository
git clone <your-repo-url>
cd DoAnCN

# 2. Tạo file .env
cp .env.example .env
# Sửa OPENAI_API_KEY trong file .env

# 3. Khởi động services
docker-compose up -d

# 4. Truy cập ứng dụng
# Frontend: http://localhost:5174
# Backend:  http://localhost:5000
# Chatbot:  http://localhost:5001
```

### Với Local Development
```bash
# 1. Setup và start tất cả services
python main.py setup
python main.py start

# 2. Hoặc start từng service riêng
python main.py backend    # Port 5000
python main.py chatbot    # Port 5001  
python main.py frontend   # Port 5174

# 3. Check status
python main.py status
```

## 📋 API Documentation

Hệ thống cung cấp RESTful API hoàn chỉnh:

- 📖 **API Docs**: http://localhost:5000/api/docs
- 🩺 **Health Check**: http://localhost:5000/api/health
- 📄 **Full API List**: Xem [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)

### API Endpoints chính:

```bash
# Authentication
POST /api/auth/register    # Đăng ký tài khoản
POST /api/auth/login       # Đăng nhập

# Invoices Management  
GET    /api/invoices       # Danh sách hóa đơn
POST   /api/invoices       # Tạo hóa đơn mới
GET    /api/invoices/{id}  # Chi tiết hóa đơn
PUT    /api/invoices/{id}  # Cập nhật hóa đơn
DELETE /api/invoices/{id}  # Xóa hóa đơn

# OCR Processing
POST /api/ocr/process      # Xử lý hình ảnh OCR

# Analytics & Reports
GET /api/analytics/dashboard      # Dashboard statistics
GET /api/analytics/revenue        # Báo cáo doanh thu
GET /api/analytics/customer-analytics  # Phân tích khách hàng
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