"""
Quick test script to check database content
"""

import psycopg2
from psycopg2.extras import RealDictCursor

try:
    conn = psycopg2.connect(
        "postgresql://postgres:123@localhost:5432/ocr_database",
        cursor_factory=RealDictCursor
    )
    
    with conn.cursor() as cursor:
        # Count invoices
        cursor.execute("SELECT COUNT(*) as count FROM invoices")
        result = cursor.fetchone()
        total = result['count']
        
        print(f"📊 Database has {total} invoices")
        
        if total > 0:
            # Show first 5 invoices
            cursor.execute("""
                SELECT filename, invoice_code, buyer_name, total_amount, created_at
                FROM invoices
                ORDER BY created_at DESC
                LIMIT 5
            """)
            
            print("\n🧾 Recent invoices:")
            for inv in cursor.fetchall():
                print(f"  • {inv['filename']}")
                print(f"    Code: {inv['invoice_code']}")
                print(f"    Buyer: {inv['buyer_name']}")
                print(f"    Amount: {inv['total_amount']}")
                print(f"    Date: {inv['created_at']}")
                print()
        else:
            print("\n⚠️ Database is EMPTY!")
            print("Need to:")
            print("1. Upload invoice image to backend")
            print("2. Backend will process OCR")
            print("3. Data will be saved to database")
    
    conn.close()
    print("✅ Database connection test successful")
    
except Exception as e:
    print(f"❌ Database error: {e}")
