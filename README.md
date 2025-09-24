# Invoice Management System with AI Chatbot 🤖

Hệ thống quản lý hóa đơn thông minh với AI chatbot tích hợp, được container hóa hoàn toàn với Docker.

## 🚀 Khởi động nhanh với Docker

### Yêu cầu hệ thống

- Docker >= 20.10
- Docker Compose >= 2.0

### Khởi động toàn bộ hệ thống

```bash
# Clone repository
git clone <repository-url>
cd DoAnCN

# Khởi động tất cả services
./start.sh start

# Hoặc sử dụng docker-compose trực tiếp
docker-compose up -d
```

### Truy cập ứng dụng

- **Frontend**: http://localhost:5174
- **Backend API**: http://localhost:5000
- **Chatbot API**: http://localhost:5001
- **Database Management**: http://localhost:5050 (PgAdmin)

### Lệnh hữu ích

```bash
# Xem logs
./start.sh logs

# Dừng services
./start.sh stop

# Khởi động với dev tools
./start.sh tools

# Kiểm tra health
./start.sh health
```

📖 **Chi tiết**: Xem [DOCKER_README.md](DOCKER_README.md) để biết thêm thông tin.

---

## 🏗️ Kiến trúc hệ thống

### Services chính

- **Backend** (Flask): API chính và business logic
- **Frontend** (React): Giao diện người dùng
- **Chatbot** (Flask): AI chatbot với training data
- **PostgreSQL**: Database chính
- **MongoDB**: Training data cho AI
- **Redis**: Cache và sessions

### Tính năng nổi bật

- ✅ Quản lý hóa đơn toàn diện
- ✅ AI Chatbot học từ dữ liệu
- ✅ OCR xử lý hình ảnh
- ✅ Template system linh hoạt
- ✅ Real-time notifications
- ✅ Docker containerization

---

## 📋 Cài đặt truyền thống (không Docker)

### Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Chatbot

```bash
cd chatbot
pip install -r requirements.txt
python app.py
```

---

## 🔧 Cấu hình

### Environment Variables

Tạo file `.env` trong thư mục gốc:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/invoice_db
MONGODB_URL=mongodb://localhost:27017/

# AI
OPENAI_API_KEY=your-api-key-here

# Security
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
```

### Database Setup

```bash
# PostgreSQL
createdb invoice_app
psql invoice_app < schema.sql

# MongoDB (tự động tạo khi chạy)
```

---

## 🧪 Testing

### Chạy tests

```bash
# Backend tests
cd backend && python -m pytest

# Với Docker
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

---

## 📁 Cấu trúc dự án

```
DoAnCN/
├── backend/              # Flask API backend
│   ├── models/          # Database models
│   ├── routes/          # API endpoints
│   ├── services/        # Business logic
│   └── Dockerfile
├── frontend/            # React frontend
│   ├── src/
│   └── Dockerfile
├── chatbot/             # AI Chatbot service
│   ├── handlers/        # Chat logic
│   ├── models/          # AI models
│   └── Dockerfile
├── rasa/                # NLP processing (optional)
├── docker-compose.yml   # Docker orchestration
├── start.sh            # Startup script
└── DOCKER_README.md    # Docker documentation
```

---

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

---

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 📞 Liên hệ

- **Project Link**: [GitHub Repository]
- **Issues**: [GitHub Issues]

---

## 🙏 Acknowledgments

- [Flask](https://flask.palletsprojects.com/) - Web framework
- [React](https://reactjs.org/) - Frontend library
- [MongoDB](https://www.mongodb.com/) - NoSQL database
- [PostgreSQL](https://www.postgresql.org/) - SQL database
- [Docker](https://www.docker.com/) - Containerization

---

**Made with ❤️ by Khahoang1107**
