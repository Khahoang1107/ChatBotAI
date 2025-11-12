#!/usr/bin/env python3
"""
Create Admin User Script
========================

Script để tạo tài khoản admin đầu tiên cho hệ thống.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.database_tools import get_database_tools
from models.user import User, UserRole
from utils.auth_utils import get_password_hash

def create_admin_user():
    """Tạo tài khoản admin đầu tiên"""
    print("🔧 Creating admin user...")

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
            # Check if admin user already exists
            cursor.execute("SELECT id FROM users WHERE role = %s", (UserRole.ADMIN.value,))
            if cursor.fetchone():
                print("⚠️ Admin user already exists")
                return True

            # Create admin user
            admin_username = "admin"
            admin_email = "admin@example.com"
            admin_password = "admin123"  # Change this in production!

            password_hash = get_password_hash(admin_password)

            cursor.execute("""
                INSERT INTO users (username, email, password_hash, full_name, role, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                admin_username,
                admin_email,
                password_hash,
                "System Administrator",
                UserRole.ADMIN.value,
                True,
                "NOW()"
            ))

            result = cursor.fetchone()
            if result:
                admin_id = result[0]
                conn.commit()
                print("✅ Admin user created successfully!")
                print(f"   Username: {admin_username}")
                print(f"   Email: {admin_email}")
                print(f"   Password: {admin_password}")
                print(f"   Role: {UserRole.ADMIN.value}")
                print(f"   User ID: {admin_id}")
                print("\n🔐 Please change the default password after first login!")
                return True
            else:
                print("❌ Failed to create admin user")
                return False

    except Exception as e:
        print(f"❌ Error creating admin user: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = create_admin_user()
    sys.exit(0 if success else 1)