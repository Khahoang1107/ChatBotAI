# Tính năng Quản lý và Xuất Hóa đơn

## 🎯 Tổng quan

Tính năng mới cho phép người dùng:
- Xem danh sách hóa đơn dạng **bảng tính** (spreadsheet view)
- **Tìm kiếm** và **lọc** hóa đơn
- **Chọn nhiều** hóa đơn để xuất
- **Xuất báo cáo** ra file **Excel** hoặc **PDF**

## 📋 Cách sử dụng

### 1. Truy cập trang Quản lý Hóa đơn

Có 3 cách để vào trang này:

#### Cách 1: Qua Chat Commands
Gõ một trong các lệnh sau trong chat:
```
- "xuất báo cáo"
- "xuất excel"
- "xuất pdf"
- "quản lý hóa đơn"
```

#### Cách 2: Qua Quick Action Buttons
1. Gõ "Chatbot có thể làm gì?"
2. Nhấn nút **"📊 Xuất báo cáo"**

#### Cách 3: Từ danh sách hóa đơn
Khi xem danh sách hóa đơn trong chat, có thể gõ "xuất file" để chuyển sang trang quản lý

---

## 🖥️ Giao diện Quản lý Hóa đơn

### Header Actions
- **← Quay lại**: Trở về Dashboard
- **📊 Xuất Excel**: Xuất hóa đơn đã chọn ra file CSV (mở được bằng Excel)
- **📄 Xuất PDF**: Xuất hóa đơn ra PDF (đang phát triển)

### Thanh công cụ
1. **🔍 Tìm kiếm**: 
   - Tìm theo mã hóa đơn
   - Tìm theo tên người mua
   - Tìm theo tên người bán

2. **📁 Lọc loại**:
   - Tất cả loại
   - Hóa đơn điện (⚡)
   - MoMo (💳)
   - Thông thường (📄)

3. **✅ Checkbox**:
   - Chọn/bỏ chọn tất cả
   - Chọn từng hóa đơn riêng lẻ

### Bảng dữ liệu

| Cột | Mô tả |
|-----|-------|
| ☑️ | Checkbox để chọn hóa đơn |
| STT | Số thứ tự |
| Mã hóa đơn | Mã định danh duy nhất |
| Ngày | Ngày phát hành |
| Người bán | Tên công ty/cá nhân bán |
| Người mua | Tên khách hàng |
| Số tiền | Tổng giá trị (VND) |
| Loại | Icon loại hóa đơn |
| Độ tin cậy | % độ chính xác OCR |
| Xử lý lúc | Thời gian xử lý |

### Thống kê dưới bảng

4 khối thống kê hiển thị:
- **Tổng số hóa đơn**: Số lượng đang hiển thị
- **Tổng giá trị**: Tổng tiền của các hóa đơn
- **Độ tin cậy TB**: Trung bình độ tin cậy
- **Đã chọn**: Số hóa đơn được chọn

---

## 📊 Xuất file Excel

### Cách xuất:

1. **Chọn hóa đơn** (tùy chọn):
   - Tick checkbox các hóa đơn muốn xuất
   - Hoặc bỏ qua để xuất tất cả

2. **Nhấn nút "Xuất Excel"**

3. **File được tải xuống**:
   - Format: `invoices_YYYY-MM-DD.csv`
   - Encoding: UTF-8 with BOM (mở được tiếng Việt)
   - Mở bằng: Excel, Google Sheets, LibreOffice

### Cấu trúc file Excel:

```csv
STT,Mã hóa đơn,Ngày,Người bán,Người mua,Số tiền,Loại,Độ tin cậy,Trạng thái,Xử lý lúc
1,PB16010051828,10/11/2025,Công ty Điện lực,Pham Van Giau,294948,Hóa đơn điện,75.0%,processed,04/12/2025 18:02:15
2,INV-12345,...
```

### Lưu ý:
- File CSV có thể mở trực tiếp bằng Excel
- Nếu tiếng Việt bị lỗi, chọn **Data > From Text/CSV** trong Excel và chọn encoding UTF-8

---

## 🎨 Giao diện Features

### Màu sắc Độ tin cậy:
- 🟢 **Xanh lá** (≥80%): Độ tin cậy cao
- 🟡 **Vàng** (60-79%): Độ tin cậy trung bình
- 🔴 **Đỏ** (<60%): Độ tin cậy thấp, cần kiểm tra

### Icons Loại hóa đơn:
- ⚡ **Điện**: Hóa đơn thanh toán điện
- 💳 **MoMo**: Thanh toán qua MoMo
- 📄 **Thông thường**: Hóa đơn chung

### Responsive Design:
- Bảng có thanh cuộn ngang trên mobile
- Tối ưu cho màn hình 1024px+
- Hover effects cho dễ xem

---

## 💾 Database Backend

### Table: `invoices`
Mỗi hóa đơn xử lý sẽ được lưu vào SQLite database:

```sql
CREATE TABLE invoices (
    id INTEGER PRIMARY KEY,
    invoice_code TEXT,
    date TEXT,
    buyer_name TEXT,
    seller_name TEXT,
    total_amount TEXT,
    total_amount_value REAL,
    invoice_type TEXT,
    confidence REAL,
    processed_at TIMESTAMP,
    -- ... more fields
);
```

### API Endpoint:
```
GET /api/invoices
Authorization: Bearer {token}

Response:
{
    "invoices": [...],
    "total": 10
}
```

---

## 🔧 Technical Details

### Frontend:
- **File**: `frontend/src/pages/InvoiceManagement.tsx`
- **Framework**: React + TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Export**: Browser-based CSV generation

### State Management:
```typescript
const [currentView, setCurrentView] = useState<'dashboard' | 'invoices'>('dashboard');
```

### Navigation Flow:
```
Dashboard (Chat) 
    → Command: "xuất báo cáo"
    → setCurrentView('invoices')
    → InvoiceManagement Component
    → Click "Quay lại"
    → setCurrentView('dashboard')
```

---

## 🚀 Future Enhancements

### Planned Features:
1. ✅ **PDF Export** - Xuất báo cáo PDF với template đẹp
2. ✅ **Email Reports** - Gửi báo cáo qua email
3. ✅ **Advanced Filters** - Lọc theo khoảng thời gian, giá trị
4. ✅ **Charts/Analytics** - Biểu đồ thống kê chi tiết
5. ✅ **Bulk Actions** - Xóa, cập nhật nhiều hóa đơn cùng lúc
6. ✅ **Invoice Details Modal** - Xem chi tiết từng hóa đơn
7. ✅ **Sorting** - Sắp xếp theo cột
8. ✅ **Pagination** - Phân trang khi có nhiều hóa đơn

---

## 📝 Notes

- Database file: `backend/invoices.db`
- Backend cần chạy với Tesseract OCR để độ chính xác cao
- File CSV dùng BOM để Excel tự động nhận UTF-8
- Responsive design tối ưu cho desktop

---

## 🐛 Troubleshooting

### 1. Không thấy hóa đơn?
- Kiểm tra đã upload và xử lý hóa đơn chưa
- Kiểm tra backend đang chạy
- Xem console browser có lỗi API không

### 2. File Excel lỗi font?
- Mở Excel → Data → From Text/CSV
- Chọn file → Origin: UTF-8
- Load data

### 3. Xuất PDF không hoạt động?
- Tính năng đang phát triển
- Tạm thời xuất Excel rồi chuyển sang PDF

---

## 📞 Support

Nếu có vấn đề, gõ trong chat:
```
"hướng dẫn xuất báo cáo"
"hướng dẫn sử dụng"
```

Hoặc liên hệ: user@invoice.com
