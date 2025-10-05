"""
Create database schema for OCR invoices
"""

import psycopg2

print("🔧 Creating PostgreSQL database schema...")

try:
    # Connect to database
    conn = psycopg2.connect(
        "postgresql://postgres:123@localhost:5432/ocr_database"
    )
    conn.autocommit = True
    
    cursor = conn.cursor()
    
    # Create invoices table
    print("\n📋 Creating 'invoices' table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id SERIAL PRIMARY KEY,
            filename VARCHAR(255) NOT NULL,
            invoice_code VARCHAR(100),
            invoice_type VARCHAR(50),
            invoice_date VARCHAR(50),
            buyer_name VARCHAR(255),
            buyer_tax_code VARCHAR(50),
            buyer_address TEXT,
            seller_name VARCHAR(255),
            seller_tax_code VARCHAR(50),
            seller_address TEXT,
            subtotal VARCHAR(100),
            tax_amount VARCHAR(100),
            total_amount VARCHAR(100),
            currency VARCHAR(10),
            confidence_score DECIMAL(3,2),
            raw_text TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)
    print("✅ Table 'invoices' created successfully")
    
    # Create index for faster queries
    print("\n📑 Creating indexes...")
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_invoices_filename 
        ON invoices(filename)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_invoices_created_at 
        ON invoices(created_at DESC)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_invoices_buyer_name 
        ON invoices(buyer_name)
    """)
    print("✅ Indexes created successfully")
    
    # Check table
    cursor.execute("""
        SELECT COUNT(*) FROM invoices
    """)
    count = cursor.fetchone()[0]
    print(f"\n📊 Current invoice count: {count}")
    
    # Insert sample data if empty
    if count == 0:
        print("\n📝 Inserting sample invoice data...")
        cursor.execute("""
            INSERT INTO invoices (
                filename, invoice_code, invoice_type, invoice_date,
                buyer_name, seller_name, total_amount, currency,
                confidence_score, raw_text
            ) VALUES 
            (
                'sample-invoice-001.jpg',
                'INV-2025-001',
                'general',
                '01/10/2025',
                'CÔNG TY TNHH MẪU',
                'CÔNG TY CỔ PHẦN DỊCH VỤ',
                '5,000,000 VND',
                'VND',
                0.95,
                'Sample invoice data for testing'
            ),
            (
                'sample-invoice-002.jpg',
                'INV-2025-002',
                'electricity',
                '30/09/2025',
                'HỘ GIA ĐÌNH NGUYỄN VĂN A',
                'CÔNG TY ĐIỆN LỰC',
                '1,500,000 VND',
                'VND',
                0.92,
                'Electricity bill sample'
            )
        """)
        
        cursor.execute("SELECT COUNT(*) FROM invoices")
        new_count = cursor.fetchone()[0]
        print(f"✅ Inserted {new_count} sample invoices")
    
    cursor.close()
    conn.close()
    
    print("\n" + "="*60)
    print("✅ DATABASE SCHEMA CREATED SUCCESSFULLY!")
    print("="*60)
    print("\n📋 Table structure:")
    print("   - id: Primary key (auto-increment)")
    print("   - filename: Image filename")
    print("   - invoice_code: Invoice number")
    print("   - invoice_type: Type of invoice")
    print("   - buyer_name, seller_name: Parties")
    print("   - total_amount: Invoice amount")
    print("   - confidence_score: OCR confidence")
    print("   - created_at: Timestamp")
    print("\n🚀 Ready to use!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nMake sure:")
    print("   1. PostgreSQL is running")
    print("   2. Database 'ocr_database' exists")
    print("   3. User 'postgres' password is '123'")
