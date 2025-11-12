#!/usr/bin/env python3
"""Reset OCR jobs table"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=int(os.getenv('DB_PORT', 5432)),
    database=os.getenv('DB_NAME', 'ocr_database_new'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', '123')
)

cur = conn.cursor()

print("🔧 Resetting OCR jobs with transaction errors...")

# Delete failed/stuck jobs
cur.execute("DELETE FROM ocr_jobs WHERE status IN ('processing', 'failed') OR attempts > 2")
print(f"   Deleted {cur.rowcount} stuck jobs")

# Reset all queued jobs
cur.execute("UPDATE ocr_jobs SET attempts = 0 WHERE status = 'queued'")
print(f"   Reset {cur.rowcount} queued jobs")

conn.commit()

# Show remaining jobs
cur.execute("SELECT COUNT(*) as total, COUNT(CASE WHEN status='queued' THEN 1 END) as queued FROM ocr_jobs")
total, queued = cur.fetchone()
print(f"\n✅ OCR jobs table reset:")
print(f"   Total jobs: {total}")
print(f"   Queued jobs: {queued}")

cur.close()
conn.close()
