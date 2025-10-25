#!/usr/bin/env python3
"""Fix ocr_jobs table schema - add missing columns"""

import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Import directly
import importlib.util
spec = importlib.util.spec_from_file_location("database", os.path.join(backend_path, "utils", "database.py"))
database = importlib.util.module_from_spec(spec)
spec.loader.exec_module(database)
get_db = database.get_db

def fix_schema():
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Check existing columns
        cur.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name='ocr_jobs' AND column_name='attempts'
        """)
        if not cur.fetchone():
            print("❌ 'attempts' column missing - adding it...")
            cur.execute("ALTER TABLE ocr_jobs ADD COLUMN attempts INT DEFAULT 0")
            conn.commit()
            print("✅ Added 'attempts' column")
        else:
            print("✅ 'attempts' column exists")
        
        # Check progress column
        cur.execute("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name='ocr_jobs' AND column_name='progress'
        """)
        if not cur.fetchone():
            print("❌ 'progress' column missing - adding it...")
            cur.execute("ALTER TABLE ocr_jobs ADD COLUMN progress INT DEFAULT 0")
            conn.commit()
            print("✅ Added 'progress' column")
        else:
            print("✅ 'progress' column exists")
        
        # List all columns
        print("\n📋 Current ocr_jobs columns:")
        cur.execute("""
            SELECT column_name, data_type FROM information_schema.columns 
            WHERE table_name='ocr_jobs' ORDER BY ordinal_position
        """)
        for col_name, col_type in cur.fetchall():
            print(f"   • {col_name}: {col_type}")
        
        print("\n✅ Schema fixed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()
    
    return True

if __name__ == "__main__":
    fix_schema()
