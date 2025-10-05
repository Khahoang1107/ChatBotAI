"""
Quick check PostgreSQL connection and data
"""

import psycopg2
from psycopg2.extras import RealDictCursor

print("=" * 70)
print("🔍 KIỂM TRA POSTGRESQL CONNECTION & DATA")
print("=" * 70)

# Connection info
db_info = {
    'host': 'localhost',
    'port': '5432',
    'database': 'ocr_database',
    'user': 'postgres',
    'password': '123'
}

print(f"\n📡 Thông tin kết nối:")
print(f"   Host: {db_info['host']}")
print(f"   Port: {db_info['port']}")
print(f"   Database: {db_info['database']}")
print(f"   User: {db_info['user']}")

try:
    # Connect
    print(f"\n🔌 Đang kết nối PostgreSQL...")
    conn = psycopg2.connect(
        host=db_info['host'],
        port=db_info['port'],
        database=db_info['database'],
        user=db_info['user'],
        password=db_info['password'],
        cursor_factory=RealDictCursor
    )
    
    print(f"✅ KẾT NỐI THÀNH CÔNG!")
    
    cursor = conn.cursor()
    
    # Check tables
    print(f"\n📋 Danh sách bảng trong database:")
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cursor.fetchall()
    
    if tables:
        for table in tables:
            print(f"   ✓ {table['table_name']}")
    else:
        print(f"   ⚠️ Chưa có bảng nào!")
    
    # Check invoices table
    print(f"\n📊 Kiểm tra bảng 'invoices':")
    try:
        cursor.execute("SELECT COUNT(*) as count FROM invoices")
        count = cursor.fetchone()['count']
        print(f"   ✅ Bảng tồn tại")
        print(f"   📈 Tổng số hóa đơn: {count}")
        
        if count > 0:
            # Show sample data
            print(f"\n📄 Dữ liệu mẫu (5 hóa đơn gần nhất):")
            cursor.execute("""
                SELECT 
                    id, 
                    filename, 
                    invoice_code, 
                    invoice_type,
                    buyer_name, 
                    seller_name, 
                    total_amount,
                    confidence_score,
                    created_at
                FROM invoices 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            
            invoices = cursor.fetchall()
            for idx, inv in enumerate(invoices, 1):
                print(f"\n   {idx}. 🧾 {inv['filename']}")
                print(f"      ├─ Mã HĐ: {inv['invoice_code']}")
                print(f"      ├─ Loại: {inv['invoice_type']}")
                print(f"      ├─ Khách hàng: {inv['buyer_name']}")
                print(f"      ├─ Nhà cung cấp: {inv['seller_name']}")
                print(f"      ├─ Tổng tiền: {inv['total_amount']}")
                print(f"      ├─ Độ tin cậy: {float(inv['confidence_score'])*100:.0f}%")
                print(f"      └─ Ngày tạo: {inv['created_at']}")
        else:
            print(f"\n   ⚠️ Bảng trống! Chưa có dữ liệu.")
            print(f"   💡 Upload ảnh hóa đơn để thêm dữ liệu.")
        
        # Statistics
        if count > 0:
            print(f"\n📈 Thống kê:")
            
            # By type
            cursor.execute("""
                SELECT invoice_type, COUNT(*) as count 
                FROM invoices 
                GROUP BY invoice_type
            """)
            types = cursor.fetchall()
            print(f"   Phân loại:")
            for t in types:
                print(f"      • {t['invoice_type']}: {t['count']} hóa đơn")
            
            # Average confidence
            cursor.execute("""
                SELECT AVG(confidence_score) as avg_conf
                FROM invoices
            """)
            avg_conf = cursor.fetchone()['avg_conf']
            print(f"   Độ tin cậy TB: {float(avg_conf)*100:.1f}%")
            
    except Exception as e:
        print(f"   ❌ Lỗi: {e}")
        print(f"   💡 Bảng 'invoices' chưa được tạo. Chạy: python create_schema.py")
    
    cursor.close()
    conn.close()
    
    print(f"\n" + "=" * 70)
    print(f"✅ KIỂM TRA HOÀN TẤT - DATABASE HOẠT ĐỘNG BÌNH THƯỜNG")
    print(f"=" * 70)
    
except psycopg2.OperationalError as e:
    print(f"\n❌ KHÔNG KẾT NỐI ĐƯỢC POSTGRESQL!")
    print(f"\n🔴 Lỗi: {e}")
    print(f"\n💡 Kiểm tra:")
    print(f"   1. PostgreSQL đang chạy? (pgAdmin hoặc services.msc)")
    print(f"   2. Port 5432 đang mở?")
    print(f"   3. Database 'ocr_database' đã tạo?")
    print(f"   4. Password đúng là '123'?")
    print(f"\n🔧 Tạo database nếu chưa có:")
    print(f"   CREATE DATABASE ocr_database;")
    
except Exception as e:
    print(f"\n❌ LỖI: {e}")
    print(f"\n💡 Kiểm tra lại thông tin kết nối.")

print()
