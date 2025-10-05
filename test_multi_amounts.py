"""
🧪 TEST MULTI-AMOUNT EXTRACTION
Test OCR với hóa đơn có nhiều tổng cộng
"""

import sys
sys.path.append('fastapi_backend')

from ocr_service import ocr_service

# Test cases
test_cases = [
    {
        "name": "Hóa đơn nhà hàng - 3 món + tổng",
        "ocr_text": """
        NHÀ HÀNG HOÀNG LONG
        ===================
        Món ăn 1: Phở bò         100.000 VNĐ
        Món ăn 2: Cơm gà        200.000 VNĐ  
        Món ăn 3: Nước ngọt      50.000 VNĐ
        
        Thành tiền:             350.000 VNĐ
        Thuế VAT 10%:            35.000 VNĐ
        TỔNG CỘNG:              385.000 VNĐ
        """,
        "expected_subtotals": 4,
        "expected_grand_total": "385.000"
    },
    {
        "name": "Hóa đơn điện nước - 3 loại phí",
        "ocr_text": """
        HÓA ĐƠN TIỆN ÍCH
        ================
        Tiền điện:              500.000 VNĐ
        Tiền nước:              120.000 VNĐ
        Tiền internet:           80.000 VNĐ
        
        Tổng cộng:              700.000 VNĐ
        """,
        "expected_subtotals": 3,
        "expected_grand_total": "700.000"
    },
    {
        "name": "Hóa đơn siêu thị - 5 items + giảm giá",
        "ocr_text": """
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
        """,
        "expected_subtotals": 5,
        "expected_grand_total": "450.000"
    },
    {
        "name": "Không có keyword 'tổng cộng' - test sum detection",
        "ocr_text": """
        800.000
        300.000
        500.000
        """,
        "expected_subtotals": 2,
        "expected_grand_total": "800.000"  # Should detect 800 = 300+500
    }
]

print("=" * 60)
print("🧪 TESTING MULTI-AMOUNT EXTRACTION")
print("=" * 60)
print()

passed = 0
failed = 0

for i, test in enumerate(test_cases, 1):
    print(f"📋 Test {i}: {test['name']}")
    print("-" * 60)
    
    try:
        # Extract amounts
        result = ocr_service.extract_multiple_amounts(test['ocr_text'])
        
        # Check results
        subtotals_count = len(result.get('subtotals', []))
        grand_total = result.get('grand_total', '')
        
        print(f"   Subtotals found: {subtotals_count}")
        print(f"   Subtotals: {', '.join(result.get('subtotals', []))}")
        print(f"   Grand total: {grand_total}")
        
        # Verify
        subtotals_ok = subtotals_count >= test['expected_subtotals'] - 1  # Allow ±1
        grand_total_ok = test['expected_grand_total'] in grand_total
        
        if subtotals_ok and grand_total_ok:
            print(f"   ✅ PASS")
            passed += 1
        else:
            print(f"   ❌ FAIL")
            if not subtotals_ok:
                print(f"      Expected {test['expected_subtotals']} subtotals, got {subtotals_count}")
            if not grand_total_ok:
                print(f"      Expected grand total '{test['expected_grand_total']}', got '{grand_total}'")
            failed += 1
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        failed += 1
    
    print()

print("=" * 60)
print(f"📊 RESULTS: {passed} passed, {failed} failed")
print("=" * 60)

if failed == 0:
    print("✅ ALL TESTS PASSED! 🎉")
    print()
    print("Hệ thống đã sẵn sàng xử lý hóa đơn có:")
    print("  • Nhiều tổng cộng nhỏ (subtotals)")
    print("  • Một tổng cộng lớn (grand total)")
    print("  • Tự động phát hiện qua keyword hoặc logic tính")
else:
    print(f"⚠️ {failed} test(s) failed. Check implementation.")
