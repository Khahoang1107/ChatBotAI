#!/usr/bin/env python3
"""
Create a user account for the AI Invoice Assistant
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.utils.auth_service import auth_service
from backend.models.user import UserCreate

def create_user():
    """Create a new user account"""

    print("🆕 Tạo tài khoản đăng nhập mới")
    print("=" * 40)

    # Get user input
    username = input("Tên đăng nhập: ").strip()
    if not username:
        print("❌ Tên đăng nhập không được để trống")
        return

    email = input("Email: ").strip()
    if not email:
        print("❌ Email không được để trống")
        return

    password = input("Mật khẩu: ").strip()
    if not password:
        print("❌ Mật khẩu không được để trống")
        return

    full_name = input("Họ tên đầy đủ (tùy chọn): ").strip()

    # Create user data
    user_data = UserCreate(
        username=username,
        email=email,
        password=password,
        full_name=full_name if full_name else None
    )

    try:
        # Register user
        user = auth_service.register_user(user_data)

        print("\n✅ Tài khoản đã được tạo thành công!")
        print(f"   👤 Tên đăng nhập: {user.username}")
        print(f"   📧 Email: {user.email}")
        print(f"   👨‍💼 Họ tên: {user.full_name or 'Chưa cập nhật'}")
        print(f"   📅 Ngày tạo: {user.created_at}")
        print(f"   🔢 ID: {user.id}")

        print("\n🔐 Bạn có thể đăng nhập bằng:")
        print(f"   Username: {user.username}")
        print(f"   Password: {password}")

    except Exception as e:
        print(f"\n❌ Lỗi tạo tài khoản: {str(e)}")

if __name__ == "__main__":
    create_user()