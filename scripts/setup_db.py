#!/usr/bin/env python3
"""
Setup database tables for OCR system
"""

import psycopg2
import sys

try:
    # Connect to database
    conn = psycopg2.connect('postgresql://postgres:123@localhost:5432/ocr_database')
    cur = conn.cursor()
    
    # Read and execute SQL migration
    with open('backend/sql/create_ocr_jobs.sql', 'r') as f:
        sql = f.read()
    
    cur.execute(sql)
    conn.commit()
    
    print("✅ Database tables created successfully!")
    print("   - ocr_jobs table")
    print("   - ocr_notifications table")
    print("   - Indexes created")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
