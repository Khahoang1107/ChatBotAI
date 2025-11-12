#!/usr/bin/env python
"""Add missing columns to ocr_jobs table"""

import psycopg2

conn = psycopg2.connect(
    "postgresql://postgres:123@localhost:5432/ocr_database_new"
)
cursor = conn.cursor()

try:
    # Check if progress column exists
    cursor.execute("""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name='ocr_jobs' AND column_name='progress'
    """)
    
    if not cursor.fetchone():
        print("[*] Adding progress column...")
        cursor.execute("""
            ALTER TABLE ocr_jobs ADD COLUMN progress INTEGER DEFAULT 0
        """)
        conn.commit()
        print("[+] progress column added")
    else:
        print("[+] progress column already exists")
    
    # List all columns
    cursor.execute("""
        SELECT column_name, data_type FROM information_schema.columns 
        WHERE table_name='ocr_jobs'
        ORDER BY ordinal_position
    """)
    
    print("\n[+] ocr_jobs table columns:")
    for col_name, data_type in cursor.fetchall():
        print(f"    - {col_name}: {data_type}")
    
    cursor.close()
    conn.close()
    print("\n[+] Schema update completed!")
    
except Exception as e:
    print(f"[-] Error: {e}")
    conn.rollback()

