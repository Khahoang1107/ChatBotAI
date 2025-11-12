#!/usr/bin/env python3
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', 5432),
    database=os.getenv('DB_NAME', 'ocr_database_new'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', '123')
)

cur = conn.cursor()

# Add attempts column if missing
try:
    cur.execute('ALTER TABLE ocr_jobs ADD COLUMN attempts INT DEFAULT 0')
    print('✅ Added attempts column')
except psycopg2.Error:
    print('✅ attempts column already exists')

# Add progress column if missing  
try:
    cur.execute('ALTER TABLE ocr_jobs ADD COLUMN progress INT DEFAULT 0')
    print('✅ Added progress column')
except psycopg2.Error:
    print('✅ progress column already exists')

conn.commit()

# Show all columns
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='ocr_jobs' ORDER BY ordinal_position")
print('\n📋 ocr_jobs columns:')
for (col,) in cur.fetchall():
    print(f'   • {col}')

cur.close()
conn.close()
print('\n✅ Schema fixed!')
