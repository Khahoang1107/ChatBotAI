# Backend API Service

Backend API cho hệ thống quản lý hóa đơn và OCR với Flask/FastAPI.

## 📋 Tính năng

- 🔐 **Authentication**: JWT authentication và user management
- 📄 **Invoice Management**: CRUD operations cho hóa đơn
- 🤖 **OCR Integration**: API xử lý ảnh và trích xuất thông tin
- 📊 **Template System**: Quản lý mẫu hóa đơn
- 💾 **Database**: PostgreSQL/SQLite với SQLAlchemy ORM
- 📈 **Analytics**: Thống kê và báo cáo
- 🔍 **Search**: Tìm kiếm và lọc dữ liệu

## 🏗️ Cấu trúc

```
backend/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── models/              # Database models
│   ├── __init__.py
│   ├── user.py          # User model
│   ├── invoice.py       # Invoice model
│   └── template.py      # Template model
├── routes/              # API routes
│   ├── __init__.py
│   ├── auth.py          # Authentication routes
│   ├── invoices.py      # Invoice CRUD
│   ├── templates.py     # Template management
│   └── ocr.py           # OCR processing
├── services/            # Business logic
│   ├── __init__.py
│   ├── auth_service.py  # Authentication logic
│   ├── ocr_service.py   # OCR processing
│   └── email_service.py # Email notifications
├── utils/               # Utilities
│   ├── __init__.py
│   ├── database.py      # Database connection
│   ├── decorators.py    # Custom decorators
│   └── helpers.py       # Helper functions
├── migrations/          # Database migrations
└── tests/               # Unit tests
    ├── test_auth.py
    ├── test_invoices.py
    └── test_ocr.py
```

## 🚀 Cài đặt

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Chỉnh sửa .env với thông tin database và API keys
python app.py
```

## 📡 API Endpoints

### Authentication

- `POST /api/auth/register` - Đăng ký user mới
- `POST /api/auth/login` - Đăng nhập
- `POST /api/auth/refresh` - Refresh token
- `POST /api/auth/logout` - Đăng xuất

### Invoices

- `GET /api/invoices` - Lấy danh sách hóa đơn
- `POST /api/invoices` - Tạo hóa đơn mới
- `GET /api/invoices/{id}` - Lấy chi tiết hóa đơn
- `PUT /api/invoices/{id}` - Cập nhật hóa đơn
- `DELETE /api/invoices/{id}` - Xóa hóa đơn

### Templates

- `GET /api/templates` - Lấy danh sách templates
- `POST /api/templates` - Tạo template mới
- `GET /api/templates/{id}` - Lấy chi tiết template
- `DELETE /api/templates/{id}` - Xóa template
- `GET /api/templates/ocr-ready` - Templates sẵn sàng OCR

### OCR

- `POST /api/ocr/process` - Xử lý ảnh OCR
- `GET /api/ocr/history` - Lịch sử OCR
- `POST /api/ocr/batch` - Xử lý nhiều ảnh

### Analytics

- `GET /api/analytics/dashboard` - Dashboard statistics
- `GET /api/analytics/invoices` - Invoice analytics
- `GET /api/analytics/ocr` - OCR analytics

## 🔧 Configuration

Environment variables trong `.env`:

```
DATABASE_URL=postgresql://user:pass@localhost/dbname
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
OPENAI_API_KEY=your-openai-key
FLASK_ENV=development
```

## 🗄️ Database Schema

Sử dụng SQLAlchemy ORM với các models:

- **Users**: Authentication và user profiles
- **Invoices**: Thông tin hóa đơn
- **Templates**: Mẫu hóa đơn
- **OCR_Results**: Kết quả xử lý OCR
- **Audit_Logs**: Logging hệ thống
