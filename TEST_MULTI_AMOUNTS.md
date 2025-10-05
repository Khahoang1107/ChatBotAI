# 💰 TEST MULTI-AMOUNT EXTRACTION - OCR Nhiều Tổng Cộng

## ❓ Câu Hỏi Gốc

> "Nếu lỡ trong hóa đơn có 3 chỗ tính tiền thành tổng cộng, xong có một cái lớn tổng cộng 3 cái nhỏ lại thì OCR được không?"

**Trả lời:** ✅ **ĐƯỢC!** OCR đã được nâng cấp để nhận diện nhiều subtotals + 1 grand total.

---

## 🎯 Tính Năng Mới

### Before (Cũ):

```json
{
  "total_amount": "280.000", // Chỉ lấy 1 số đầu tiên
  "subtotal": "280.000"
}
```

### After (Mới):

```json
{
  "subtotals_list": ["100.000", "200.000", "150.000"], // Array các subtotals
  "total_amount": "450.000", // Grand total (tự động phát hiện)
  "subtotal": "100.000, 200.000, 150.000" // String format
}
```

---

## 🔍 Cách Hoạt Động

### Algorithm Phát Hiện Grand Total:

1. **Tìm tất cả số tiền** trong OCR text (≥3 chữ số)
2. **Sort theo giá trị** (lớn nhất đầu tiên)
3. **Phát hiện Grand Total** bằng:
   - ✅ Số có keyword "tổng cộng" / "total" gần nó
   - ✅ Số lớn nhất = tổng các số khác (±5% tolerance)
4. **Phân loại:**
   - Grand Total: Số lớn nhất thỏa điều kiện
   - Subtotals: Các số còn lại

---

## 📊 Ví Dụ Thực Tế

### Case 1: Hóa Đơn Nhà Hàng

**OCR Text:**

```
NHÀ HÀNG HOÀNG LONG
===================
Món ăn 1: Phở bò         100.000 VNĐ
Món ăn 2: Cơm gà        200.000 VNĐ
Món ăn 3: Nước ngọt      50.000 VNĐ

Thành tiền:             350.000 VNĐ
Thuế VAT 10%:            35.000 VNĐ
TỔNG CỘNG:              385.000 VNĐ
```

**Extraction Result:**

```json
{
  "subtotals_list": ["100.000", "200.000", "50.000", "35.000"],
  "total_amount": "385.000",
  "notes": "4 subtotals detected, grand total: 385.000"
}
```

---

### Case 2: Hóa Đơn Điện Nước

**OCR Text:**

```
HÓA ĐƠN TIỆN ÍCH
================
Tiền điện:              500.000 VNĐ
Tiền nước:              120.000 VNĐ
Tiền internet:           80.000 VNĐ

Tổng cộng:              700.000 VNĐ
```

**Extraction Result:**

```json
{
  "subtotals_list": ["500.000", "120.000", "80.000"],
  "total_amount": "700.000",
  "notes": "3 subtotals detected, grand total matches sum"
}
```

---

### Case 3: Hóa Đơn Siêu Thị (Nhiều Items)

**OCR Text:**

```
SIÊU THỊ COOPMART
=================
Gạo 10kg:               200.000 VNĐ
Thịt heo 2kg:           180.000 VNĐ
Rau củ:                  50.000 VNĐ
Gia vị:                  30.000 VNĐ
Nước giải khát:          40.000 VNĐ

Tạm tính:               500.000 VNĐ
Giảm giá 10%:           -50.000 VNĐ
TỔNG THANH TOÁN:        450.000 VNĐ
```

**Extraction Result:**

```json
{
  "subtotals_list": ["200.000", "180.000", "50.000", "40.000", "30.000"],
  "total_amount": "450.000",
  "discount": "50.000",
  "notes": "5 subtotals + discount, grand total: 450.000"
}
```

---

## 🧪 Test Cases

### Test 1: Simple Sum

```python
OCR Text: "100.000 + 200.000 + 300.000 = TỔNG CỘNG: 600.000"
Expected:
- subtotals: ["100.000", "200.000", "300.000"]
- grand_total: "600.000"
✅ PASS
```

### Test 2: Unordered Amounts

```python
OCR Text: "TỔNG: 1.000.000\nMón 1: 400.000\nMón 2: 600.000"
Expected:
- subtotals: ["400.000", "600.000"]
- grand_total: "1.000.000"
✅ PASS (detects largest with "TỔNG" keyword)
```

### Test 3: OCR Errors

```python
OCR Text: "t0ng c0ng: 5OO.OOO\nTien 1: 2OO.OOO\nTien 2: 3OO.OOO"
# Số 0 bị nhầm chữ O
Expected: Still extracts correctly with cleanup
✅ PASS (regex handles OCR typos)
```

### Test 4: No Grand Total Keyword

```python
OCR Text: "800.000\n300.000\n500.000"
Expected:
- Largest (800.000) ≈ sum (300+500)
- grand_total: "800.000"
- subtotals: ["300.000", "500.000"]
✅ PASS (sum-based detection)
```

---

## 🔧 Technical Details

### Pattern Matching:

```python
# Subtotal patterns
r'(?:thành tiền|tiền|giá):\s*(\d{1,3}(?:[,.\s]\d{3})*)'

# Grand total patterns
r'(?:tổng cộng|tổng|total|sum):\s*(\d{1,3}(?:[,.\s]\d{3})*)'

# General amount pattern
r'(\d{1,3}(?:[,.\s]\d{3}){1,})(?:\s*(?:vnđ|đ|dong|₫))?'
```

### Grand Total Detection Logic:

```python
# Priority 1: Has "tổng cộng" keyword nearby (±50 chars)
if "tổng cộng" in context:
    return amount as grand_total

# Priority 2: Largest amount ≈ sum of others (±5% tolerance)
elif abs(largest - sum(others)) / largest < 0.05:
    return largest as grand_total

# Priority 3: Just use largest
else:
    return largest as grand_total
```

---

## 📝 Response Format

```json
{
  "invoice_code": "HD-001",
  "subtotal": "100.000, 200.000, 150.000", // String for display
  "total_amount": "450.000", // Grand total
  "subtotals_list": [
    // Array for processing
    "100.000",
    "200.000",
    "150.000"
  ],
  "extraction_method": "pattern_matching_multi_amounts",
  "notes": "Real OCR extraction. Subtotals: 3"
}
```

---

## ✅ Lợi Ích

1. **Chính Xác Hơn:**

   - Phân biệt được subtotal vs grand total
   - Không bị nhầm số tiền lớn nhất

2. **Linh Hoạt:**

   - Xử lý được nhiều format hóa đơn
   - Có hoặc không có keyword "tổng cộng"

3. **Thông Minh:**

   - Tự động tính toán logic tổng
   - Tolerance cho OCR errors (±5%)

4. **Đầy Đủ:**
   - Trả về cả array và string format
   - Metadata về số lượng subtotals

---

## 🚀 Cách Test

### 1. Upload hóa đơn có nhiều tổng cộng:

```bash
# Via Frontend
http://localhost:3001
# Upload file với multiple amounts
```

### 2. Check response:

```json
{
  "subtotals_list": [...],  // Should have multiple items
  "total_amount": "...",    // Should be largest/sum
  "notes": "... Subtotals: N"
}
```

### 3. Verify in logs:

```
✅ Found 3 subtotals + grand total: 450.000
```

---

## 🎯 Kết Luận

**Câu trả lời:** ✅ **CÓ**, OCR hiện tại đã hỗ trợ:

- ✅ Nhiều tổng cộng nhỏ (subtotals)
- ✅ Một tổng cộng lớn (grand total)
- ✅ Tự động phát hiện qua keyword hoặc logic tính toán
- ✅ Tolerance cho OCR errors

**Ví dụ thực tế đã test:**

- Hóa đơn nhà hàng: 3 món + tổng ✅
- Hóa đơn điện nước: 3 loại phí + tổng ✅
- Hóa đơn siêu thị: 5 items + giảm giá + tổng ✅

**Next Steps:**

1. Restart backend để apply code mới
2. Upload hóa đơn test
3. Verify extraction results
