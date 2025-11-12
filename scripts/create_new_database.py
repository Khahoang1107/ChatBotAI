#!/usr/bin/env python
"""
Tạo database mới và reset schema
"""

import psycopg2
from psycopg2 import sql
import os

# Database connection info
DB_HOST = "localhost"
DB_PORT = 5432
DB_USER = "postgres"
DB_PASSWORD = "123"
DB_NAME = "ocr_database_new"

def create_new_database():
    """Tạo database mới"""
    try:
        # Connect to default postgres database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("[*] Checking if database exists...")
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        exists = cursor.fetchone()
        
        if exists:
            print(f"[!] Database '{DB_NAME}' already exists. Dropping it...")
            cursor.execute(f"DROP DATABASE IF EXISTS {DB_NAME}")
            print(f"[+] Database dropped")
        
        print(f"[*] Creating new database '{DB_NAME}'...")
        cursor.execute(f"CREATE DATABASE {DB_NAME}")
        print(f"[+] Database '{DB_NAME}' created successfully")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"[-] Error creating database: {e}")
        return False

def create_tables():
    """Tạo schema cho database mới"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        
        # Create invoices table
        print("[*] Creating invoices table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id SERIAL PRIMARY KEY,
                filename VARCHAR(255),
                invoice_code VARCHAR(100),
                invoice_type VARCHAR(50),
                buyer_name VARCHAR(255),
                seller_name VARCHAR(255),
                invoice_date DATE,
                total_amount VARCHAR(50),
                confidence_score FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("[+] Invoices table created")
        
        # Create OCR jobs table
        print("[*] Creating ocr_jobs table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ocr_jobs (
                id UUID PRIMARY KEY,
                filepath VARCHAR(500),
                filename VARCHAR(255),
                status VARCHAR(50) DEFAULT 'queued',
                result TEXT,
                error_message TEXT,
                invoice_id INTEGER REFERENCES invoices(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)
        print("[+] OCR jobs table created")
        
        # Create index on status for faster polling
        print("[*] Creating index on ocr_jobs(status)...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ocr_jobs_status 
            ON ocr_jobs(status)
        """)
        print("[+] Index created")
        
        # Create OCR notifications table
        print("[*] Creating ocr_notifications table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ocr_notifications (
                id SERIAL PRIMARY KEY,
                job_id UUID REFERENCES ocr_jobs(id),
                event_type VARCHAR(50),
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("[+] Notifications table created")
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"[-] Error creating tables: {e}")
        return False

def insert_sample_data():
    """Insert sample invoices"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        
        print("[*] Inserting sample invoices...")
        
        samples = [
            ("invoice_001.pdf", "INV-2025-001", "electricity", "Công ty ABC", "Công ty điện lực", "2025-10-01", "1,500,000", 0.95),
            ("invoice_002.pdf", "INV-2025-002", "water", "Công ty XYZ", "Công ty nước sạch", "2025-10-05", "500,000", 0.90),
            ("invoice_003.pdf", "INV-2025-003", "sale", "Cửa hàng ABC", "Nhà cung cấp hàng", "2025-10-10", "10,000,000", 0.92),
        ]
        
        for filename, code, inv_type, buyer, seller, date, amount, confidence in samples:
            cursor.execute("""
                INSERT INTO invoices 
                (filename, invoice_code, invoice_type, buyer_name, seller_name, invoice_date, total_amount, confidence_score)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (filename, code, inv_type, buyer, seller, date, amount, confidence))
        
        conn.commit()
        print(f"[+] Inserted {len(samples)} sample invoices")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"[-] Error inserting data: {e}")
        return False

def verify_database():
    """Verify database created successfully"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        
        print("\n[*] Verifying database...")
        
        # Count invoices
        cursor.execute("SELECT COUNT(*) FROM invoices")
        invoice_count = cursor.fetchone()[0]
        print(f"[+] Invoices table: {invoice_count} records")
        
        # Show all tables
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema='public'
        """)
        tables = [row[0] for row in cursor.fetchall()]
        print(f"[+] Tables: {', '.join(tables)}")
        
        cursor.close()
        conn.close()
        
        print(f"\n[+] Database '{DB_NAME}' ready to use!")
        print(f"    Connection: postgresql://{DB_USER}:***@{DB_HOST}:{DB_PORT}/{DB_NAME}")
        
        return True
        
    except Exception as e:
        print(f"[-] Error verifying database: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Creating New Database and Schema")
    print("=" * 60)
    
    success = True
    
    # Step 1: Create database
    if not create_new_database():
        success = False
    
    # Step 2: Create tables
    if success and not create_tables():
        success = False
    
    # Step 3: Insert sample data
    if success and not insert_sample_data():
        success = False
    
    # Step 4: Verify
    if success and not verify_database():
        success = False
    
    if success:
        print("\n[+] Database setup completed successfully!")
    else:
        print("\n[-] Database setup failed!")
    
    print("=" * 60)

