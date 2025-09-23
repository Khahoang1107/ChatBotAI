# Rasa ChatBot cho Xử Lý Hóa Đơn

Hệ thống chatbot NLP sử dụng Rasa để hỗ trợ xử lý hóa đơn điện tử, OCR và quản lý template.

## 🚀 Cài Đặt và Chạy

### Windows

```bash
# Chạy script setup
setup.bat

# Huấn luyện model
rasa train

# Khởi động Rasa server (terminal 1)
rasa run --enable-api --cors "*" --port 5005

# Khởi động Action server (terminal 2)
rasa run actions --port 5055
```

### Linux/Mac

```bash
# Chạy script setup
chmod +x setup.sh
./setup.sh

# Huấn luyện model
rasa train

# Khởi động Rasa server (terminal 1)
rasa run --enable-api --cors "*" --port 5005

# Khởi động Action server (terminal 2)
rasa run actions --port 5055
```

## 📋 Tính Năng

### Intents (Ý định)

- `greet`: Chào hỏi
- `goodbye`: Tạm biệt
- `ask_invoice_help`: Hỏi về hỗ trợ hóa đơn
- `create_invoice_template`: Tạo mẫu hóa đơn
- `extract_invoice_data`: Trích xuất dữ liệu OCR
- `search_invoice`: Tìm kiếm hóa đơn
- `upload_invoice`: Tải lên hóa đơn

### Entities (Thực thể)

- `invoice_number`: Số hóa đơn
- `company_name`: Tên công ty
- `customer_name`: Tên khách hàng
- `amount`: Số tiền
- `date`: Ngày tháng
- `template_name`: Tên mẫu
- `file_type`: Loại file

### Custom Actions

- `action_create_template`: Tạo mẫu hóa đơn mới
- `action_process_ocr`: Xử lý OCR hình ảnh
- `action_search_invoice`: Tìm kiếm hóa đơn
- `action_list_templates`: Liệt kê mẫu có sẵn
- `action_handle_upload`: Xử lý upload file
- `action_train_rasa`: Huấn luyện lại model

## 🔗 Tích Hợp Backend

Chatbot kết nối với backend API qua các endpoints:

- `POST /api/templates` - Tạo mẫu hóa đơn
- `GET /api/templates` - Lấy danh sách mẫu
- `GET /api/invoices/search` - Tìm kiếm hóa đơn
- `POST /api/templates/rasa/train` - Huấn luyện Rasa

## 🌍 Hỗ Trợ Tiếng Việt

- Pipeline NLP được cấu hình cho tiếng Việt
- Sử dụng spaCy model `vi_core_news_lg`
- Training data bằng tiếng Việt
- Responses bằng tiếng Việt

## 🧪 Test Chatbot

### Command Line

```bash
rasa shell
```

### Web Interface

Sau khi khởi động server, chatbot có thể được tích hợp vào frontend qua REST API:

```
POST http://localhost:5005/webhooks/rest/webhook
```

### Ví dụ Request

```json
{
  "sender": "user123",
  "message": "Tôi muốn tạo mẫu hóa đơn"
}
```

## 📁 Cấu Trúc File

```
rasa/
├── config.yml          # Cấu hình pipeline và policies
├── domain.yml          # Định nghĩa intents, entities, responses
├── endpoints.yml       # Cấu hình endpoints
├── requirements.txt    # Dependencies Python
├── setup.bat/.sh       # Scripts cài đặt
├── data/
│   ├── nlu.yml         # Training data cho NLU
│   ├── stories.yml     # Conversation flows
│   └── rules.yml       # Business rules
├── actions/
│   └── actions.py      # Custom actions
└── models/             # Trained models (sau khi train)
```

## 🔄 Quy Trình Hoạt Động

1. **User**: Gửi tin nhắn tiếng Việt
2. **NLU**: Phân tích intent và entities
3. **Core**: Quyết định action tiếp theo
4. **Actions**: Thực hiện custom actions (gọi API backend)
5. **Response**: Trả về phản hồi cho user

## 📊 Monitoring

- Logs được lưu trong thư mục `logs/`
- Có thể sử dụng Rasa X để monitoring và cải thiện model
- Tích hợp với backend để track usage và performance
