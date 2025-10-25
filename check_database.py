#!/usr/bin/env python
"""Check database content and OCR worker status"""

import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect(
    "postgresql://postgres:123@localhost:5432/ocr_database_new",
    cursor_factory=RealDictCursor
)
cursor = conn.cursor()

print("[*] Checking database content...")
print("=" * 70)

# Check invoices
cursor.execute("SELECT COUNT(*) as count FROM invoices")
inv_count = cursor.fetchone()
print(f"\n[+] INVOICES TABLE: {inv_count['count']} records")

# Show invoices
cursor.execute("SELECT id, filename, invoice_code, buyer_name, total_amount FROM invoices LIMIT 5")
invoices = cursor.fetchall()
if invoices:
    print(f"\n    Sample invoices:")
    for inv in invoices:
        print(f"    - ID: {inv['id']:2d} | Code: {inv['invoice_code']:15s} | Buyer: {inv['buyer_name']:20s} | Amount: {inv['total_amount']}")
else:
    print("    No invoices yet")

# Check OCR jobs
cursor.execute("SELECT COUNT(*) as count FROM ocr_jobs")
ocr_count = cursor.fetchone()
print(f"\n[+] OCR JOBS TABLE: {ocr_count['count']} records")

# Check OCR job statuses
cursor.execute("SELECT status, COUNT(*) as count FROM ocr_jobs GROUP BY status")
statuses = cursor.fetchall()
if statuses:
    print(f"\n    Job statuses:")
    for status in statuses:
        print(f"    - {status['status']:10s}: {status['count']} jobs")
else:
    print("    No OCR jobs yet")

# Show recent OCR jobs
cursor.execute("""
    SELECT id, filename, status, created_at 
    FROM ocr_jobs 
    ORDER BY created_at DESC 
    LIMIT 5
""")
recent_jobs = cursor.fetchall()
if recent_jobs:
    print(f"\n    Recent OCR jobs:")
    for job in recent_jobs:
        print(f"    - {str(job['id'])[:8]}... | {job['filename']:30s} | Status: {job['status']:10s} | Created: {job['created_at']}")

# Check OCR notifications
cursor.execute("SELECT COUNT(*) as count FROM ocr_notifications")
notif_count = cursor.fetchone()
print(f"\n[+] OCR NOTIFICATIONS TABLE: {notif_count['count']} records")

cursor.close()
conn.close()

print("\n" + "=" * 70)
print("[+] Database connection OK!")
print("[+] Database ready for OCR processing")

