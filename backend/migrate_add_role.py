#!/usr/bin/env python3
"""
Database Migration: Add Role Column
===================================

Migration để thêm role column vào users table và update existing users.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.database_tools import get_database_tools
from models.user import UserRole

def migrate_add_role_column():
    """Thêm role column vào users table"""
    print("🔄 Migrating database: Adding role column...")

    # Get database tools
    db_tools = get_database_tools()
    if not db_tools:
        print("❌ Database tools not available")
        return False

    conn = db_tools.connect()
    if not conn:
        print("❌ Database connection failed")
        return False

    try:
        with conn.cursor() as cursor:
            # Check if role column already exists
            cursor.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'users' AND column_name = 'role'
            """)

            if cursor.fetchone():
                print("⚠️ Role column already exists")
                return True

            # Add role column
            cursor.execute("""
                ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'user'
            """)
            print("✅ Added role column to users table")

            # Update existing users: set is_admin users to admin role
            cursor.execute("""
                UPDATE users SET role = 'admin' WHERE is_admin = true
            """)
            updated_count = cursor.rowcount
            print(f"✅ Updated {updated_count} existing admin users")

            # Set remaining users to user role
            cursor.execute("""
                UPDATE users SET role = 'user' WHERE role IS NULL OR role = ''
            """)
            updated_count = cursor.rowcount
            print(f"✅ Updated {updated_count} users to user role")

            # Make role column NOT NULL
            cursor.execute("""
                ALTER TABLE users ALTER COLUMN role SET NOT NULL
            """)
            print("✅ Made role column NOT NULL")

            # Add check constraint for valid roles
            cursor.execute("""
                ALTER TABLE users ADD CONSTRAINT check_role
                CHECK (role IN ('user', 'admin'))
            """)
            print("✅ Added role validation constraint")

            conn.commit()
            print("✅ Migration completed successfully!")
            return True

    except Exception as e:
        print(f"❌ Migration error: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = migrate_add_role_column()
    sys.exit(0 if success else 1)