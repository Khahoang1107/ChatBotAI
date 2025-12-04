# Cấu trúc File Excel Xuất Hóa Đơn

## 📊 Tổng quan

File Excel được xuất ra từ trang **Quản lý Hóa đơn** bao gồm **20 cột** với đầy đủ thông tin chi tiết của mỗi hóa đơn.

---

## 📋 Danh sách 20 cột trong Excel

### Cột 1-4: Thông tin cơ bản
| # | Tên cột | Mô tả | Ví dụ |
|---|----------|-------|-------|
| 1 | **STT** | Số thứ tự | 1, 2, 3... |
| 2 | **Mã hóa đơn** | Mã định danh duy nhất | PB16010051828 |
| 3 | **Ngày** | Ngày phát hành | 10/11/2025 |
| 4 | **Loại hóa đơn** | Loại (text đầy đủ) | Hóa đơn điện, Thanh toán MoMo, Hóa đơn thông thường |

### Cột 5-7: Thông tin người bán
| # | Tên cột | Mô tả | Ví dụ |
|---|----------|-------|-------|
| 5 | **Người bán** | Tên công ty/cá nhân | Công ty Điện lực |
| 6 | **Địa chỉ người bán** | Địa chỉ đầy đủ | 123 Đường ABC, TP.HCM |
| 7 | **MST người bán** | Mã số thuế | 0123456789 |

### Cột 8-10: Thông tin người mua
| # | Tên cột | Mô tả | Ví dụ |
|---|----------|-------|-------|
| 8 | **Người mua** | Tên khách hàng | Pham Van Giau |
| 9 | **Địa chỉ người mua** | Địa chỉ khách hàng | Hoa Thuan, Tinh Vinh |
| 10 | **MST người mua** | Mã số thuế khách | 9876543210 |

### Cột 11-15: Chi tiết tài chính
| # | Tên cột | Mô tả | Ví dụ |
|---|----------|-------|-------|
| 11 | **Tiền trước thuế** | Subtotal | 266,317 |
| 12 | **Thuế VAT** | Số tiền thuế | 26,631 |
| 13 | **% Thuế** | Phần trăm thuế | 10% |
| 14 | **Tổng tiền** | Tổng cộng | 294,948 |
| 15 | **Đơn vị tiền** | Currency | VND |

### Cột 16-18: Thông tin kỹ thuật
| # | Tên cột | Mô tả | Ví dụ |
|---|----------|-------|-------|
| 16 | **Độ tin cậy** | Confidence score | 75.0% |
| 17 | **Phương thức OCR** | OCR method | OCR (Tesseract), Metadata |
| 18 | **Tên file gốc** | Original filename | z7217936890941_a7a00b6124ed02007ddb1a129457c188.jpg |

### Cột 19-20: Trạng thái
| # | Tên cột | Mô tả | Ví dụ |
|---|----------|-------|-------|
| 19 | **Trạng thái** | Status | processed, pending, failed |
| 20 | **Xử lý lúc** | Timestamp | 04/12/2025 18:17:24 |

---

## 📝 Ví dụ dòng dữ liệu

```csv
STT,Mã hóa đơn,Ngày,Loại hóa đơn,Người bán,Địa chỉ người bán,MST người bán,Người mua,Địa chỉ người mua,MST người mua,Tiền trước thuế,Thuế VAT,% Thuế,Tổng tiền,Đơn vị tiền,Độ tin cậy,Phương thức OCR,Tên file gốc,Trạng thái,Xử lý lúc
1,"PB16010051828","10/11/2025","Hóa đơn điện","Công ty Điện lực","","","Pham Van Giau","Hoa Thuan, Tinh Vinh","",266317,26631,"10%",294948,"VND","75.0%","OCR (Tesseract)","z7217936890941_a7a00b6124ed02007ddb1a129457c188.jpg","processed","04/12/2025 18:17:24"
```

---

## 🎯 Lợi ích của 20 cột

### ✅ Đầy đủ thông tin
- **Không thiếu** bất kỳ trường nào quan trọng
- **Dễ phân tích** với Excel PivotTable
- **Sẵn sàng** cho báo cáo kế toán

### ✅ Hỗ trợ lọc và tìm kiếm
- Lọc theo **Loại hóa đơn** (cột 4)
- Lọc theo **MST** (cột 7, 10)
- Lọc theo **Phương thức OCR** (cột 17)
- Lọc theo **Độ tin cậy** (cột 16)

### ✅ Phân tích tài chính
- Tính tổng **Tiền trước thuế** (cột 11)
- Tính tổng **Thuế VAT** (cột 12)
- Tính tổng **Tổng tiền** (cột 14)
- So sánh % thuế giữa các hóa đơn

### ✅ Kiểm toán và truy xuất
- **Tên file gốc** (cột 18) để tìm lại ảnh
- **Xử lý lúc** (cột 20) để theo dõi timeline
- **Độ tin cậy** (cột 16) để đánh giá chất lượng OCR

---

## 🔧 Cách sử dụng file Excel

### 1. Mở file CSV bằng Excel

**Nếu tiếng Việt hiển thị sai:**

```
Excel → Data → From Text/CSV
→ Chọn file
→ File Origin: UTF-8
→ Load
```

### 2. Lọc dữ liệu

- Nhấn **Data → Filter**
- Click icon ▼ ở header mỗi cột
- Chọn giá trị muốn lọc

**Ví dụ lọc:**
- Lọc **Loại hóa đơn = "Hóa đơn điện"**
- Lọc **Độ tin cậy ≥ 80%**
- Lọc **Phương thức OCR = "OCR (Tesseract)"**

### 3. Tính tổng

Chọn cột số (11, 12, 14), Excel tự động hiện tổng ở góc dưới

**Hoặc dùng công thức:**
```excel
=SUM(K2:K100)  // Tổng tiền trước thuế
=SUM(L2:L100)  // Tổng thuế VAT
=SUM(N2:N100)  // Tổng cộng tất cả
```

### 4. Tạo PivotTable

```
Insert → PivotTable
→ Chọn range
→ Rows: Loại hóa đơn
→ Values: Sum of Tổng tiền
```

Kết quả: Tổng tiền theo từng loại hóa đơn

### 5. Tạo biểu đồ

```
Insert → Chart
→ Chọn loại biểu đồ (Pie, Bar, Line...)
→ Chọn dữ liệu từ cột Loại và Tổng tiền
```

---

## 📊 Các trường hợp xuất dữ liệu

### Xuất tất cả hóa đơn
1. Không chọn checkbox nào
2. Nhấn **"Xuất Excel"**
3. Tất cả hóa đơn trong bảng được xuất

### Xuất hóa đơn đã chọn
1. Tick checkbox các hóa đơn cần xuất
2. Nhấn **"Xuất Excel"**
3. Chỉ các hóa đơn đã chọn được xuất

### Xuất sau khi lọc
1. Dùng ô tìm kiếm hoặc dropdown lọc loại
2. Bảng chỉ hiển thị hóa đơn đã lọc
3. Nhấn **"Xuất Excel"**
4. Chỉ hóa đơn đang hiển thị được xuất

---

## 💡 Tips & Tricks

### Định dạng số trong Excel

**Format tiền:**
```
Chọn cột số → Right-click → Format Cells
→ Number → Decimal places: 0
→ Use 1000 separator: ✓
→ OK
```

**Format phần trăm:**
```
Cột % Thuế đã là text "10%"
Nếu muốn tính toán: =VALUE(LEFT(M2, LEN(M2)-1))/100
```

### Tìm hóa đơn có vấn đề

**Độ tin cậy thấp:**
```
Filter → Độ tin cậy → Text Filters → Less Than
→ Nhập: 70%
```

**Thiếu MST:**
```
Filter → MST người bán → (Blanks)
```

**Không dùng OCR:**
```
Filter → Phương thức OCR → Equals → "Metadata"
```

### Export một phần dữ liệu

**Chỉ xuất thông tin cơ bản (6 cột):**
- Trong Excel: Xóa các cột không cần
- Hoặc copy 6 cột sang sheet mới
- Save as CSV mới

---

## 🔍 So sánh với file Excel cũ

| Tính năng | Excel cũ (10 cột) | Excel mới (20 cột) |
|-----------|-------------------|-------------------|
| **Thông tin người bán** | Tên | Tên + Địa chỉ + MST |
| **Thông tin người mua** | Tên | Tên + Địa chỉ + MST |
| **Chi tiết tài chính** | Tổng tiền | Subtotal + Tax + Total + Currency |
| **Loại hóa đơn** | Icon emoji | Text đầy đủ (có thể lọc) |
| **Kỹ thuật** | Độ tin cậy | Độ tin cậy + OCR method + Filename |
| **Có thể lọc theo loại** | ❌ | ✅ |
| **Có thể phân tích thuế** | ❌ | ✅ |
| **Truy xuất file gốc** | ❌ | ✅ |

---

## 📞 Hỗ trợ

Nếu cần thêm cột hoặc thay đổi format, liên hệ:
- Email: user@invoice.com
- Hoặc gõ trong chat: "hướng dẫn xuất excel"

---

## 🎓 Kết luận

File Excel 20 cột cung cấp:
- ✅ **Đầy đủ** thông tin hóa đơn
- ✅ **Dễ lọc** theo nhiều tiêu chí
- ✅ **Hỗ trợ phân tích** tài chính
- ✅ **Sẵn sàng** cho kiểm toán
- ✅ **Truy xuất** file ảnh gốc

**Không còn thiếu thông tin quan trọng nào!** 🎉
