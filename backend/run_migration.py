#!/usr/bin/env python3
"""
Run database migrations for the chatbot system
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from utils.database_tools import get_database_tools

def run_migration():
    """Run the database migration"""
    try:
        db = get_database_tools()
        conn = db.connect()

        if not conn:
            print("❌ Cannot connect to database")
            return False

        cursor = conn.cursor()

        # Read and execute migration file
        migration_file = os.path.join(os.path.dirname(__file__), 'sql', 'add_users_and_chat_history.sql')

        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()

        print("📋 Running migration...")
        cursor.execute(migration_sql)
        conn.commit()

        print("✅ Migration completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)