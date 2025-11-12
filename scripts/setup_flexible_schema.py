"""Check and update database schema for flexible invoice data"""

import psycopg2

conn = psycopg2.connect('postgresql://postgres:123@localhost:5432/ocr_database_new')
cur = conn.cursor()

print("📋 CURRENT INVOICES TABLE SCHEMA:")
print("=" * 70)

# Check invoices table schema
cur.execute("""
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_name='invoices'
ORDER BY ordinal_position
""")

for col, dtype, nullable in cur.fetchall():
    nullable_str = 'NULL' if nullable == 'YES' else 'NOT NULL'
    print(f'{col:<30} {dtype:<20} {nullable_str}')

print("\n📋 CURRENT OCR_JOBS TABLE SCHEMA:")
print("=" * 70)

# Check ocr_jobs table schema
cur.execute("""
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_name='ocr_jobs'
ORDER BY ordinal_position
""")

for col, dtype, nullable in cur.fetchall():
    nullable_str = 'NULL' if nullable == 'YES' else 'NOT NULL'
    print(f'{col:<30} {dtype:<20} {nullable_str}')

print("\n🔧 ADDING FLEXIBLE SCHEMA SUPPORT...")
print("=" * 70)

# Add metadata column to invoices if not exists
try:
    cur.execute("""
    ALTER TABLE invoices 
    ADD COLUMN metadata JSONB DEFAULT '{}';
    """)
    conn.commit()
    print("✅ Added 'metadata' JSONB column to invoices table")
except psycopg2.Error as e:
    if "already exists" in str(e).lower():
        print("✅ 'metadata' column already exists")
    else:
        print(f"⚠️ Error: {e}")
    conn.rollback()

# Add missing columns to ocr_jobs if needed
try:
    cur.execute("ALTER TABLE ocr_jobs ADD COLUMN attempts INTEGER DEFAULT 0;")
    conn.commit()
    print("✅ Added 'attempts' column to ocr_jobs")
except psycopg2.Error as e:
    if "already exists" in str(e).lower():
        print("✅ 'attempts' column already exists")
    else:
        print(f"⚠️ Error: {e}")
    conn.rollback()

try:
    cur.execute("ALTER TABLE ocr_jobs ADD COLUMN error_message TEXT;")
    conn.commit()
    print("✅ Added 'error_message' column to ocr_jobs")
except psycopg2.Error as e:
    if "already exists" in str(e).lower():
        print("✅ 'error_message' column already exists")
    else:
        print(f"⚠️ Error: {e}")
    conn.rollback()

print("\n✅ Database schema ready for flexible invoice data!")
print("\nSchema supports:")
print("  • Fixed fields: invoice_code, buyer_name, seller_name, total_amount, etc.")
print("  • Flexible fields: metadata (JSONB) - lưu dữ liệu tùy biến")
print("\nExample metadata for different invoice types:")
print("  - Hóa đơn điện: {\"period\": \"2025-10\", \"meter_reading\": 12345}")
print("  - Hóa đơn nước: {\"period\": \"2025-10\", \"usage_volume\": 50}")
print("  - Hóa đơn bán hàng: {\"items\": [{...}], \"tax_rate\": 0.1}")

cur.close()
conn.close()
