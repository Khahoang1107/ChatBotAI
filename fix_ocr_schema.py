#!/usr/bin/env python3
"""Fix ocr_jobs table schema"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# DB connection
conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=int(os.getenv('DB_PORT', 5432)),
    database=os.getenv('DB_NAME', 'ocr_database_new'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', '123')
)

cur = conn.cursor()

print("🔧 Fixing ocr_jobs schema...")

# Check and add missing columns
try:
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='ocr_jobs' AND column_name='attempts'")
    if not cur.fetchone():
        print("   Adding 'attempts' column...")
        cur.execute("ALTER TABLE ocr_jobs ADD COLUMN attempts INT DEFAULT 0")
        conn.commit()
except:
    pass

try:
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='ocr_jobs' AND column_name='progress'")
    if not cur.fetchone():
        print("   Adding 'progress' column...")
        cur.execute("ALTER TABLE ocr_jobs ADD COLUMN progress INT DEFAULT 0")
        conn.commit()
except:
    pass

try:
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='ocr_jobs' AND column_name='started_at'")
    if not cur.fetchone():
        print("   Adding 'started_at' column...")
        cur.execute("ALTER TABLE ocr_jobs ADD COLUMN started_at TIMESTAMP NULL")
        conn.commit()
except:
    pass

try:
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='ocr_jobs' AND column_name='completed_at'")
    if not cur.fetchone():
        print("   Adding 'completed_at' column...")
        cur.execute("ALTER TABLE ocr_jobs ADD COLUMN completed_at TIMESTAMP NULL")
        conn.commit()
except:
    pass

# Show all columns
print("\n✅ Current ocr_jobs columns:")
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='ocr_jobs' ORDER BY ordinal_position")
for col_name, col_type in cur.fetchall():
    print(f"   • {col_name}: {col_type}")

# Check for any queued jobs
print("\n📊 Checking queued jobs...")
cur.execute("SELECT id, filename, status FROM ocr_jobs WHERE status='queued' LIMIT 5")
jobs = cur.fetchall()
if jobs:
    print(f"   Found {len(jobs)} queued jobs:")
    for job_id, filename, status in jobs:
        print(f"   • {job_id}: {filename} ({status})")
else:
    print("   No queued jobs")

cur.close()
conn.close()
print("\n✅ Schema fixed!")
