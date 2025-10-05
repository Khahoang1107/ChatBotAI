"""
🗄️ AUTO SETUP POSTGRESQL DATABASE
==================================
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_postgresql_database():
    """Setup PostgreSQL database tự động"""
    
    # PostgreSQL credentials - thay đổi nếu cần
    POSTGRES_HOST = 'localhost'
    POSTGRES_PORT = 5432
    POSTGRES_USER = 'postgres'
    POSTGRES_PASSWORD = 'postgres'  # Thay bằng password của bạn
    DATABASE_NAME = 'ocr_database'
    
    print("🚀 Starting PostgreSQL Database Setup...")
    print(f"📍 Host: {POSTGRES_HOST}:{POSTGRES_PORT}")
    print(f"👤 User: {POSTGRES_USER}")
    print(f"🗄️ Database: {DATABASE_NAME}")
    print("-" * 50)
    
    try:
        # Step 1: Connect to PostgreSQL server
        print("🔌 Step 1: Connecting to PostgreSQL server...")
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Get PostgreSQL version
        cursor.execute('SELECT version();')
        version = cursor.fetchone()[0]
        print(f"✅ Connected to: {version}")
        
        # Step 2: Check if database exists
        print(f"🔍 Step 2: Checking if database '{DATABASE_NAME}' exists...")
        cursor.execute(
            "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
            (DATABASE_NAME,)
        )
        exists = cursor.fetchone()
        
        if not exists:
            # Create database
            print(f"🔨 Creating database '{DATABASE_NAME}'...")
            cursor.execute(f'CREATE DATABASE {DATABASE_NAME}')
            print(f"✅ Database '{DATABASE_NAME}' created successfully!")
        else:
            print(f"ℹ️ Database '{DATABASE_NAME}' already exists")
        
        cursor.close()
        conn.close()
        
        # Step 3: Connect to new database and create tables
        print(f"🔌 Step 3: Connecting to database '{DATABASE_NAME}'...")
        db_conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database=DATABASE_NAME,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD
        )
        db_cursor = db_conn.cursor()
        
        # Step 4: Create tables
        print("🔨 Step 4: Creating tables...")
        
        # Create invoices table
        create_invoices_table = """
        CREATE TABLE IF NOT EXISTS invoices (
            id SERIAL PRIMARY KEY,
            uuid VARCHAR(255) UNIQUE DEFAULT gen_random_uuid()::text,
            filename VARCHAR(255) NOT NULL,
            file_path VARCHAR(500),
            file_size_bytes INTEGER,
            invoice_code VARCHAR(255),
            invoice_date VARCHAR(50),
            invoice_type VARCHAR(100),
            buyer_name VARCHAR(255),
            buyer_tax_code VARCHAR(50),
            buyer_address TEXT,
            seller_name VARCHAR(255),
            seller_tax_code VARCHAR(50),
            seller_address TEXT,
            subtotal VARCHAR(100),
            tax_amount VARCHAR(100),
            total_amount VARCHAR(100),
            currency VARCHAR(10) DEFAULT 'VND',
            raw_ocr_text TEXT,
            confidence_score FLOAT,
            processing_time FLOAT,
            ocr_engine VARCHAR(50),
            process_mode VARCHAR(50),
            extracted_items JSONB,
            utility_usage JSONB,
            meter_readings JSONB,
            ocr_metadata JSONB,
            chatbot_notified BOOLEAN DEFAULT FALSE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        db_cursor.execute(create_invoices_table)
        print("✅ Table 'invoices' created/verified")
        
        # Create ocr_stats table
        create_stats_table = """
        CREATE TABLE IF NOT EXISTS ocr_stats (
            id SERIAL PRIMARY KEY,
            date VARCHAR(20),
            total_processed INTEGER DEFAULT 0,
            successful_ocr INTEGER DEFAULT 0,
            failed_ocr INTEGER DEFAULT 0,
            avg_confidence FLOAT DEFAULT 0.0,
            total_processing_time FLOAT DEFAULT 0.0,
            invoice_types JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        db_cursor.execute(create_stats_table)
        print("✅ Table 'ocr_stats' created/verified")
        
        # Create indexes for better performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_invoices_invoice_code ON invoices(invoice_code);",
            "CREATE INDEX IF NOT EXISTS idx_invoices_invoice_type ON invoices(invoice_type);",
            "CREATE INDEX IF NOT EXISTS idx_invoices_created_at ON invoices(created_at);",
            "CREATE INDEX IF NOT EXISTS idx_invoices_buyer_name ON invoices(buyer_name);",
            "CREATE INDEX IF NOT EXISTS idx_ocr_stats_date ON ocr_stats(date);"
        ]
        
        for index in indexes:
            db_cursor.execute(index)
        
        print("✅ Database indexes created/verified")
        
        # Commit changes
        db_conn.commit()
        
        # Step 5: Verify setup
        print("🔍 Step 5: Verifying setup...")
        
        # Count existing records
        db_cursor.execute("SELECT COUNT(*) FROM invoices;")
        invoice_count = db_cursor.fetchone()[0]
        
        db_cursor.execute("SELECT COUNT(*) FROM ocr_stats;")
        stats_count = db_cursor.fetchone()[0]
        
        print(f"📊 Current data:")
        print(f"   - Invoices: {invoice_count}")
        print(f"   - Stats records: {stats_count}")
        
        # Test insert (sample data)
        sample_invoice = """
        INSERT INTO invoices (
            filename, invoice_code, invoice_type, buyer_name, 
            total_amount, confidence_score, notes
        ) VALUES (
            'test_setup.jpg', 'SETUP-TEST-001', 'setup_test', 
            'Test Setup User', '100,000 VND', 1.0, 
            'Database setup verification record'
        ) ON CONFLICT DO NOTHING;
        """
        
        db_cursor.execute(sample_invoice)
        db_conn.commit()
        
        # Final verification
        db_cursor.execute("SELECT id, filename, invoice_code FROM invoices ORDER BY id DESC LIMIT 1;")
        last_record = db_cursor.fetchone()
        
        if last_record:
            print(f"✅ Last record: ID={last_record[0]}, File={last_record[1]}, Code={last_record[2]}")
        
        db_cursor.close()
        db_conn.close()
        
        # Step 6: Create .env file
        print("📝 Step 6: Creating .env file...")
        env_content = f"""DATABASE_URL=postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{DATABASE_NAME}
POSTGRES_HOST={POSTGRES_HOST}
POSTGRES_PORT={POSTGRES_PORT}
POSTGRES_USER={POSTGRES_USER}
POSTGRES_PASSWORD={POSTGRES_PASSWORD}
POSTGRES_DB={DATABASE_NAME}
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ .env file created")
        
        print("-" * 50)
        print("🎉 PostgreSQL Database Setup COMPLETED!")
        print("📋 Summary:")
        print(f"   ✅ Database: {DATABASE_NAME}")
        print(f"   ✅ Tables: invoices, ocr_stats")
        print(f"   ✅ Indexes: created")
        print(f"   ✅ Connection: working")
        print(f"   ✅ Environment: configured")
        print("")
        print("🚀 Next steps:")
        print("   1. Run: poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
        print("   2. Test: http://localhost:8000/health")
        print("   3. Docs: http://localhost:8000/docs")
        
        return True
        
    except psycopg2.OperationalError as e:
        if "password authentication failed" in str(e):
            print("❌ PASSWORD ERROR!")
            print("💡 Fix: Change POSTGRES_PASSWORD in this script")
            print("💡 Or reset password: ALTER USER postgres PASSWORD 'newpassword';")
        elif "could not connect to server" in str(e):
            print("❌ CONNECTION ERROR!")
            print("💡 PostgreSQL service not running")
            print("💡 Start service: net start postgresql-x64-18")
        else:
            print(f"❌ Database connection error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    setup_postgresql_database()