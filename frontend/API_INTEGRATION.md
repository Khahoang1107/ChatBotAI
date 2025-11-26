# Frontend-Backend Integration Guide

## ✅ Đã hoàn thành

### 1. API Service Layer (`src/services/apiService.ts`)
- ✅ HTTP client với timeout
- ✅ Authentication (login, register, logout)
- ✅ Token management (localStorage)
- ✅ User profile management
- ✅ Invoice upload & management
- ✅ Chat messaging
- ✅ Health check

### 2. Auth Service Update (`src/services/authService.ts`)
- ✅ Chuyển từ mock data sang API thật
- ✅ Async login/register
- ✅ Error handling

### 3. Custom Hooks Update (`src/hooks/useAuth.ts`)
- ✅ Async state management
- ✅ Loading states
- ✅ Error handling
- ✅ Register function

### 4. Components Update
- ✅ `App.tsx` - Async login handler
- ✅ `LoginPage.tsx` - Loading state, error handling
- ✅ `UserDashboard.tsx` - Async updateUser
- ✅ Type definitions updated

### 5. Configuration
- ✅ `.env` file với backend URL
- ✅ `constants/config.ts` - API config
- ✅ Vite proxy setup cho `/api/*`

## 🚀 Cách sử dụng

### Khởi động Backend
```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

### Khởi động Frontend
```bash
cd frontend
npm run dev
```

Frontend sẽ chạy tại: `http://localhost:3000`
Backend API tại: `http://localhost:8000`

## 📋 API Endpoints đã tích hợp

### Authentication
- `POST /api/auth/register` - Đăng ký user mới
- `POST /api/auth/login` - Đăng nhập
- `GET /api/auth/me` - Lấy thông tin user hiện tại
- `PUT /api/auth/profile` - Cập nhật profile

### Invoices
- `GET /api/invoices` - Lấy danh sách hóa đơn
- `POST /api/upload` - Upload hóa đơn
- `GET /api/invoices/stats` - Thống kê hóa đơn

### Chat
- `POST /api/chat` - Gửi tin nhắn chat

### Health
- `GET /health` - Kiểm tra backend health

## 🔧 Cấu hình quan trọng

### vite.config.ts
```typescript
server: {
  port: 3000,
  open: true,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      secure: false,
    },
  },
}
```

### .env
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
VITE_ENV=development
```

## 🔐 Token Management

Token được lưu trong `localStorage` với key `token`:
- Login thành công → Save token
- Logout → Remove token
- API requests → Attach `Authorization: Bearer {token}`

## 📝 Ví dụ sử dụng

### Login
```typescript
import { apiService } from '@/services';

const handleLogin = async (email: string, password: string) => {
  try {
    const { user, token } = await apiService.login({ email, password });
    console.log('Logged in:', user);
  } catch (error) {
    console.error('Login failed:', error);
  }
};
```

### Upload Invoice
```typescript
const handleUpload = async (file: File) => {
  try {
    const result = await apiService.uploadInvoice(file);
    console.log('Upload job:', result.job_id);
  } catch (error) {
    console.error('Upload failed:', error);
  }
};
```

### Get Invoices
```typescript
const loadInvoices = async () => {
  try {
    const { invoices, total } = await apiService.getInvoices({
      skip: 0,
      limit: 10,
    });
    console.log(`Loaded ${invoices.length} of ${total} invoices`);
  } catch (error) {
    console.error('Failed to load invoices:', error);
  }
};
```

## 🐛 Debugging

### Check Backend Connection
```typescript
const checkBackend = async () => {
  try {
    const health = await apiService.healthCheck();
    console.log('Backend status:', health.status);
  } catch (error) {
    console.error('Backend not accessible:', error);
  }
};
```

### Monitor Network Requests
Mở DevTools → Network tab để xem:
- Request URL
- Headers (Authorization token)
- Response data
- Status codes

## ⚠️ Lưu ý

1. **CORS**: Backend phải enable CORS cho frontend origin
2. **Token expiry**: Cần implement token refresh logic
3. **Error handling**: Hiển thị toast notifications cho users
4. **Loading states**: UI feedback khi đang request
5. **Validation**: Client-side validation trước khi gửi API

## 🎯 Next Steps

- [ ] Thêm token refresh mechanism
- [ ] WebSocket integration cho real-time chat
- [ ] File upload progress tracking
- [ ] Offline mode support
- [ ] API response caching
- [ ] Retry logic cho failed requests
