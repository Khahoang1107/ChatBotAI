#!/usr/bin/env python3
"""
Script to promote a user to admin status
Usage: python make_admin.py <email>
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.database_tools import get_database_tools
from passlib.context import CryptContext

def make_admin(email: str):
    """Promote user to admin by email"""
    db_tools = get_database_tools()
    conn = db_tools.connect()

    if not conn:
        print("❌ Cannot connect to database")
        return False

    try:
        with conn.cursor() as cursor:
            # Check if user exists
            cursor.execute("SELECT id, username, is_admin FROM users WHERE email = %s", (email,))
            result = cursor.fetchone()

            if not result:
                print(f"❌ User with email '{email}' not found")
                return False

            user_id, username, is_admin = result

            if is_admin:
                print(f"✅ User '{username}' ({email}) is already an admin")
                return True

            # Promote to admin
            cursor.execute(
                "UPDATE users SET is_admin = TRUE WHERE id = %s",
                (user_id,)
            )
            conn.commit()

            print(f"✅ Successfully promoted user '{username}' ({email}) to admin")
            return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if 'conn' in locals() and conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python make_admin.py <email>")
        sys.exit(1)

    email = sys.argv[1]
    success = make_admin(email)

    if success:
        print("\n🎉 Admin promotion completed!")
        print("You can now login with admin privileges.")
    else:
        print("\n❌ Admin promotion failed!")
        sys.exit(1)