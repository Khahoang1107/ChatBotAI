"""
Check OCR jobs table schema and add missing columns
"""

import psycopg2

conn = psycopg2.connect('postgresql://postgres:123@localhost:5432/ocr_database_new')
cur = conn.cursor()

# Check existing columns
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='ocr_jobs' ORDER BY ordinal_position")
columns = [row[0] for row in cur.fetchall()]

print("Current OCR_JOBS columns:")
for col in columns:
    print(f"  - {col}")

# Check if 'attempts' column exists
if 'attempts' not in columns:
    print("\n⚠️ Missing 'attempts' column, adding it...")
    try:
        cur.execute("ALTER TABLE ocr_jobs ADD COLUMN attempts INTEGER DEFAULT 0")
        conn.commit()
        print("✅ Added 'attempts' column")
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()

# Check if 'error_message' column exists
if 'error_message' not in columns:
    print("\n⚠️ Missing 'error_message' column, adding it...")
    try:
        cur.execute("ALTER TABLE ocr_jobs ADD COLUMN error_message TEXT")
        conn.commit()
        print("✅ Added 'error_message' column")
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()

cur.close()
conn.close()

print("\n✅ Database schema check complete")
