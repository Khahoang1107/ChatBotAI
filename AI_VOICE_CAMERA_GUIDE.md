# 🎤📷 AI Voice Camera Control - Hướng Dẫn Sử Dụng

## 🚀 Tính Năng Mới: AI Voice Commands

Hệ thống AI của bạn giờ đây có thể **nhận diện giọng nói và tự động điều khiển camera**!

## 📋 Các Lệnh Voice Commands Khả Dụng

### 🔓 **Mở Camera**

Nói một trong các cụm từ sau để AI tự động mở camera:

```
✅ "Mở camera"
✅ "Bật camera"
✅ "Camera"
✅ "Chụp ảnh"
✅ "Chụp hình"
✅ "Open camera"
✅ "Turn on camera"
```

### 🔒 **Đóng Camera**

Nói một trong các cụm từ sau để AI tự động đóng camera:

```
✅ "Đóng camera"
✅ "Tắt camera"
✅ "Close camera"
✅ "Turn off camera"
✅ "Stop camera"
```

### 📸 **Chụp Ảnh**

Khi camera đang mở, nói một trong các cụm từ sau để chụp ảnh:

```
✅ "Chụp"
✅ "Take photo"
✅ "Capture"
✅ "Chụp hình"
```

## 🎯 Cách Sử Dụng

### Bước 1: Mở Chatbot

1. Truy cập: http://localhost:5173
2. Mở cửa sổ chatbot

### Bước 2: Kích Hoạt Mic

1. Nhấn nút 🎤 **Microphone** trong chatbot
2. Cho phép trình duyệt truy cập microphone

### Bước 3: Sử Dụng Voice Commands

1. **Nói rõ ràng**: "Mở camera"
2. **Chờ phản hồi**: AI sẽ hiển thị "🎤 Tôi đã nghe lệnh của bạn! Đang mở camera..."
3. **Camera tự mở**: Sau 1 giây, camera sẽ tự động được kích hoạt

### Bước 4: Tương Tác với Camera

- **Chụp ảnh**: Nói "Chụp" để AI tự chụp ảnh
- **Đóng camera**: Nói "Đóng camera" để AI tự đóng

## 🔧 Tính Năng Kỹ Thuật

### 🤖 **AI Processing**

```javascript
// AI Voice Command Detection Engine
const lowerTranscript = transcript.toLowerCase();

// Smart Command Recognition
const openCameraCommands = [
  "mở camera",
  "bật camera",
  "camera",
  "chụp ảnh",
  "chụp hình",
  "open camera",
];

const shouldOpenCamera = openCameraCommands.some((cmd) =>
  lowerTranscript.includes(cmd)
);
```

### 📱 **Responsive Camera Control**

- **Auto Delay**: 1 giây delay để user nghe confirmation
- **Smart Detection**: Chỉ mở camera khi chưa mở, chỉ đóng khi đang mở
- **Real-time Feedback**: AI phản hồi ngay lập tức bằng text

### 🎙️ **Voice Recognition Setup**

- **Language**: Tiếng Việt (vi-VN) + English
- **Continuous**: Luôn lắng nghe khi mic bật
- **Interim Results**: Xử lý real-time speech

## 🧪 Test Commands

### Test 1: Basic Camera Control

```
1. Nhấn mic 🎤
2. Nói: "Mở camera"
3. Xem AI phản hồi và camera mở
4. Nói: "Đóng camera"
5. Xem camera đóng
```

### Test 2: Photo Capture

```
1. Nói: "Mở camera"
2. Đợi camera sẵn sàng
3. Nói: "Chụp"
4. Xem AI chụp ảnh tự động
```

### Test 3: Multi-language

```
1. Test tiếng Việt: "Bật camera"
2. Test English: "Open camera"
3. Test mixed: "Camera on"
```

## 🎊 Ứng Dụng Thực Tế

### 📄 **OCR Hóa Đơn**

1. Nói: "Mở camera"
2. Hướng camera vào hóa đơn
3. Nói: "Chụp ảnh"
4. AI sẽ tự động OCR và trích xuất thông tin

### 💬 **Hands-free Chat**

1. Kích hoạt mic
2. Trò chuyện bằng giọng nói
3. Dùng voice commands điều khiển camera
4. Hoàn toàn không cần chạm tay

### 🏢 **Business Applications**

- **Quét hóa đơn nhanh**: Voice + Camera + OCR
- **Tư vấn khách hàng**: AI chat + visual analysis
- **Document processing**: Voice controlled scanning

## 🔍 Troubleshooting

### ❌ **Camera không mở**

- Kiểm tra quyền camera trong browser
- Thử nói rõ ràng hơn: "MỞ CAMERA"
- Đảm bảo microphone đang hoạt động

### ❌ **Voice command không nhận**

- Kiểm tra mic permissions
- Thử các từ khóa khác: "camera", "chụp ảnh"
- Nói to và rõ ràng

### ❌ **AI không phản hồi**

- Kiểm tra chatbot service: http://localhost:5001/health
- Reload trang web
- Thử nhấn mic lại

## 🎯 Tính Năng Tương Lai

- [ ] **Voice OCR**: Nói "Đọc hóa đơn" để AI tự OCR
- [ ] **Smart Templates**: "Tạo template" bằng voice
- [ ] **Voice Navigation**: Điều hướng UI bằng giọng nói
- [ ] **Multi-language**: Hỗ trợ thêm ngôn ngữ

---

## 🎉 Kết Luận

**AI Voice Camera Control** đã được tích hợp thành công! Bạn có thể:

✅ **Voice-activated camera**: Nói để mở/đóng camera  
✅ **Hands-free operation**: Hoàn toàn không cần chạm  
✅ **Smart AI responses**: Phản hồi thông minh  
✅ **Multi-language support**: Tiếng Việt + English  
✅ **Real-time processing**: Xử lý tức thì

**🎤 Thử ngay**: Mở http://localhost:5173, nhấn mic và nói "MỞ CAMERA"!
