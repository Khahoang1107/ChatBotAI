# ChatBotAI - Quick Start với Docker

## 🚀 Chạy nhanh với Docker

### Bước 1: Clone project
```bash
git clone https://github.com/YOUR_USERNAME/ChatBotAI.git
cd ChatBotAI
```

### Bước 2: Tạo file .env
```bash
# Copy file mẫu
cp .env.example .env

# Sửa file .env và thêm API keys
GROQ_API_KEY=gsk_xxxxx
GOOGLE_AI_API_KEY=AIzaSyDxxxxx
```

### Bước 3: Chạy Docker
```bash
docker-compose -f docker-compose-sqlite.yml up -d
```

### Bước 4: Truy cập
- Frontend: http://localhost:3001
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📦 Có gì trong Docker?

- ✅ Backend FastAPI (Python 3.10)
- ✅ Frontend React (Node 18)
- ✅ Tesseract OCR (hỗ trợ tiếng Việt)
- ✅ SQLite database (đã có 13 hóa đơn mẫu)
- ✅ Tài khoản test: test@example.com / password123

## 🛠️ Commands

```bash
# Xem logs
docker-compose -f docker-compose-sqlite.yml logs -f backend
docker-compose-f docker-compose-sqlite.yml logs -f frontend

# Dừng
docker-compose -f docker-compose-sqlite.yml down

# Restart
docker-compose -f docker-compose-sqlite.yml restart

# Rebuild (sau khi sửa code)
docker-compose -f docker-compose-sqlite.yml up -d --build
```

## 💾 Database

Database SQLite được mount vào container:
- File: `backend/chatbot.db`
- Backup: `database_backups/`
- Data không bị mất khi restart container!

## 🔑 Lấy API Keys (Miễn phí)

**Groq API:**
1. Truy cập https://console.groq.com
2. Sign up
3. Tạo API key

**Google AI:**
1. Truy cập https://makersuite.google.com/app/apikey
2. Tạo API key

## ✅ Hoàn tất!

Giờ bạn có thể:
1. Đăng ký tài khoản mới
2. Upload ảnh hóa đơn
3. Xem OCR tự động đọc
4. Quản lý và xuất Excel/PDF

🎉 Chúc bạn sử dụng vui vẻ!
