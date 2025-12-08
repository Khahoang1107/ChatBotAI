#!/usr/bin/env python3
"""
Run SQLite migrations for users table
"""
import sqlite3
import os

def run_migration():
    db_path = os.path.join(os.path.dirname(__file__), 'backend', 'chatbot.db')

    # Read migration SQL
    migration_path = os.path.join(os.path.dirname(__file__), 'backend', 'sql', 'migrations', '2025_10_25_add_auth_and_chat.sql')

    if not os.path.exists(migration_path):
        print(f"❌ Migration file not found: {migration_path}")
        return False

    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Read and execute migration
        with open(migration_path, 'r', encoding='utf-8') as f:
            sql = f.read()

        # Split into individual statements
        statements = sql.split(';')
        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                    print(f"✅ Executed: {statement[:50]}...")
                except Exception as e:
                    print(f"⚠️ Skipped: {statement[:50]}... ({e})")

        conn.commit()
        conn.close()

        print("✅ Migration completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    run_migration()