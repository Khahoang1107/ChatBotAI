# Chatbot Service

Dịch vụ chatbot AI hỗ trợ khách hàng và xử lý hóa đơn tự động.

## Tính năng

- 🤖 **AI Chatbot**: Trả lời câu hỏi khách hàng tự động
- 📄 **Xử lý hóa đơn**: Hỗ trợ khách hàng về thông tin hóa đơn
- 🔍 **Tìm kiếm thông minh**: Tìm kiếm thông tin trong cơ sở dữ liệu
- 📊 **Báo cáo**: Thống kê và phân tích cuộc hội thoại

## Cấu trúc thư mục

```
chatbot/
├── app.py              # Flask app chính
├── requirements.txt    # Python dependencies
├── config.py          # Cấu hình chatbot
├── models/            # Models AI và xử lý ngôn ngữ
├── handlers/          # Xử lý các loại tin nhắn
├── utils/             # Utilities và helpers
└── static/            # Static files (CSS, JS)
```

## Cài đặt

```bash
cd chatbot
pip install -r requirements.txt
python app.py
```

## API Endpoints

- `POST /chat` - Gửi tin nhắn đến chatbot
- `GET /health` - Kiểm tra trạng thái service
- `POST /webhook` - Webhook cho tích hợp bên ngoài
