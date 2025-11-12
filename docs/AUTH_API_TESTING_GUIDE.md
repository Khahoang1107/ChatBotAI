# 🚀 AI Invoice Assistant - Authentication API Documentation

## Test Guide for Login System

### 📋 Overview

Hệ thống xác thực của AI Invoice Assistant sử dụng JWT tokens với các endpoint sau:

- **POST** `/auth/register` - Đăng ký tài khoản mới
- **POST** `/auth/login` - Đăng nhập
- **GET** `/auth/me` - Lấy thông tin user hiện tại
- **POST** `/auth/logout` - Đăng xuất

### 🔗 API Documentation URLs

- **Swagger UI (Interactive)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 🧪 Test Scenarios

### 1. ✅ Health Check

**Endpoint**: `GET /health`

```bash
curl http://localhost:8000/health
```

**Expected Response**:

```json
{
  "status": "healthy",
  "service": "Invoice Chat Backend (FastAPI only)",
  "version": "2.0.0",
  "timestamp": "2025-10-25T...",
  "database": "connected",
  "chat_handlers": "initialized (disabled for now)"
}
```

### 2. 📝 User Registration

**Endpoint**: `POST /auth/register`

**Request Body**:

```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "testpass123",
  "full_name": "Test User"
}
```

**cURL Command**:

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "full_name": "Test User"
  }'
```

**Expected Response**:

```json
{
  "success": true,
  "message": "Đăng ký thành công!",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "full_name": "Test User",
    "created_at": "2025-10-25T..."
  }
}
```

### 3. 🔐 User Login

**Endpoint**: `POST /auth/login`

**Request Body**:

```json
{
  "username": "testuser",
  "password": "testpass123"
}
```

**cURL Command**:

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'
```

**Expected Response**:

```json
{
  "success": true,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "full_name": "Test User",
    "is_admin": false
  }
}
```

### 4. 👤 Get Current User Info

**Endpoint**: `GET /auth/me`

**Headers Required**:

```
Authorization: Bearer YOUR_JWT_TOKEN_HERE
```

**cURL Command**:

```bash
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

**Expected Response**:

```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "full_name": "Test User",
    "is_admin": false,
    "last_login": "2025-10-25T..."
  }
}
```

### 5. 🚪 User Logout

**Endpoint**: `POST /auth/logout`

**Headers Required**:

```
Authorization: Bearer YOUR_JWT_TOKEN_HERE
```

**cURL Command**:

```bash
curl -X POST "http://localhost:8000/auth/logout" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

**Expected Response**:

```json
{
  "success": true,
  "message": "Đăng xuất thành công"
}
```

### 6. ❌ Invalid Login Test

**Endpoint**: `POST /auth/login`

**Request Body**:

```json
{
  "username": "wronguser",
  "password": "wrongpass"
}
```

**Expected Response** (401 Unauthorized):

```json
{
  "detail": "Tên đăng nhập hoặc mật khẩu không đúng"
}
```

---

## 🛠️ Automated Testing Script

Chạy script test tự động:

```bash
cd f:\DoAnCN
python test_auth_api.py
```

Script sẽ test tất cả các endpoint authentication và báo cáo kết quả.

---

## 🔍 Error Codes & Troubleshooting

### Common HTTP Status Codes:

- **200**: Success
- **400**: Bad Request (validation error)
- **401**: Unauthorized (invalid credentials)
- **403**: Forbidden
- **404**: Not Found
- **422**: Validation Error
- **500**: Internal Server Error

### Common Issues:

1. **"Database not available"**

   - Đảm bảo PostgreSQL đang chạy
   - Kiểm tra connection string trong config

2. **"Username or email already exists"**

   - Tài khoản đã tồn tại, thử username/email khác

3. **"Could not validate credentials"**

   - Token hết hạn hoặc không hợp lệ
   - Đăng nhập lại để lấy token mới

4. **"Tên đăng nhập hoặc mật khẩu không đúng"**
   - Kiểm tra lại thông tin đăng nhập

---

## 📱 Frontend Integration

### React Login Component Usage:

```javascript
// Login function
const handleLogin = async (username, password) => {
  try {
    const response = await fetch("/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, password }),
    });

    const data = await response.json();

    if (data.success) {
      // Store token
      localStorage.setItem("token", data.access_token);
      // Redirect to dashboard
      navigate("/dashboard");
    } else {
      setError(data.detail || "Login failed");
    }
  } catch (error) {
    setError("Network error");
  }
};

// Get user info
const getUserInfo = async () => {
  const token = localStorage.getItem("token");
  if (!token) return;

  try {
    const response = await fetch("/auth/me", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const data = await response.json();
    if (data.success) {
      setUser(data.user);
    }
  } catch (error) {
    // Token expired, redirect to login
    localStorage.removeItem("token");
    navigate("/login");
  }
};
```

---

## 🔐 Security Features

- **Password Hashing**: Sử dụng bcrypt
- **JWT Tokens**: 24 giờ expiry
- **CORS**: Configured for frontend
- **Input Validation**: Pydantic models
- **SQL Injection Protection**: Parameterized queries

---

## 📊 Database Schema

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

---

## 🚀 Quick Start

1. **Start Backend**:

   ```bash
   cd backend
   python main.py
   ```

2. **Open Swagger UI**:

   - Visit: http://localhost:8000/docs

3. **Test Registration**:

   - Use Swagger UI hoặc cURL commands ở trên

4. **Test Login**:

   - Đăng nhập với tài khoản vừa tạo

5. **Test Protected Endpoints**:
   - Sử dụng JWT token từ response login

---

## 📞 Support

Nếu gặp vấn đề:

1. Kiểm tra server logs trong terminal
2. Verify database connection
3. Check network connectivity
4. Review error messages in API responses

**Happy Testing! 🎉**
