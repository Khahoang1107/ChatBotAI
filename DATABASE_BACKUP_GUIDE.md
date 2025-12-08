# 💾 Hướng dẫn Backup Database

## 🎯 Tính năng

Script tự động backup database SQLite với các tính năng:
- ✅ Tự động tạo backup với timestamp
- ✅ Giữ lại 10 bản backup gần nhất
- ✅ Khôi phục database từ backup
- ✅ Xem danh sách tất cả backup

## 📁 Vị trí

- **Database gốc**: `backend/chatbot.db`
- **Thư mục backup**: `database_backups/`
- **Script**: `backup_database.py`

## 🚀 Cách sử dụng

### 1. Tạo backup nhanh
**Cách 1**: Double-click file `backup_now.bat`

**Cách 2**: Dùng command line
```bash
cd G:\Chatbot\ChatBotAI
python backup_database.py backup
```

### 2. Xem danh sách backup
```bash
python backup_database.py list
```

### 3. Khôi phục database
**Khôi phục từ backup mới nhất:**
```bash
python backup_database.py restore
```

**Khôi phục từ file cụ thể:**
```bash
python backup_database.py restore --file chatbot_backup_20251208_190448.db
```

## 🔄 Tự động backup

### Backup tự động khi khởi động backend
Thêm vào file `backend/main.py`:

```python
# Tự động backup khi khởi động
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from backup_database import create_backup

@app.on_event("startup")
async def startup_backup():
    create_backup()
```

### Backup theo lịch (Windows Task Scheduler)
1. Mở **Task Scheduler**
2. Tạo task mới
3. Trigger: Daily lúc 23:00
4. Action: Run `backup_now.bat`

### Backup theo lịch (Python script - chạy nền)
```python
# backup_scheduler.py
import schedule
import time
from backup_database import create_backup

# Backup mỗi ngày lúc 23:00
schedule.every().day.at("23:00").do(create_backup)

# Backup mỗi 6 giờ
schedule.every(6).hours.do(create_backup)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## 📤 Upload lên GitHub

Database đã được cấu hình trong `.gitignore` để commit:

```bash
git add backend/chatbot.db database_backups/
git commit -m "Update database and backups"
git push
```

## 🔐 Bảo mật

**Quan trọng**: 
- ⚠️ Database chứa thông tin người dùng (email, password hash)
- ⚠️ Không commit vào public repo nếu có dữ liệu thật
- ✅ Dùng private repo trên GitHub
- ✅ Hoặc backup vào Google Drive/Dropbox

## 📊 Kích thước

- Database hiện tại: ~36 KB
- Mỗi backup: ~36 KB
- 10 backup: ~360 KB (rất nhẹ!)

## ❓ Troubleshooting

**Lỗi "Database không tồn tại":**
- Kiểm tra file `backend/chatbot.db` có tồn tại không
- Đảm bảo đang chạy từ thư mục gốc project

**Không thể tạo backup:**
- Kiểm tra quyền ghi vào thư mục
- Đảm bảo Python có quyền truy cập file

**Restore không thành công:**
- Kiểm tra file backup có tồn tại
- Backend phải tắt khi restore

## 🎉 Hoàn tất!

Bây giờ database của bạn sẽ được backup an toàn và có thể khôi phục bất cứ lúc nào!
