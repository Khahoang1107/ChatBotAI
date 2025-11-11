#!/usr/bin/env python3
"""
🗑️ Script xóa dữ liệu mock trong database
Xóa tất cả dữ liệu test/mock, giữ lại users thật (nếu có)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.database_tools import get_database_tools
from datetime import datetime
import shutil

def clear_mock_data():
    """Xóa tất cả dữ liệu mock trong database"""

    print("🗑️ Bắt đầu xóa dữ liệu mock...")

    db_tools = get_database_tools()
    conn = db_tools.connect()

    if not conn:
        print("❌ Không thể kết nối database")
        return False

    try:
        with conn.cursor() as cursor:
            # 1. Xóa tất cả OCR jobs (đây là test data)
            print("📋 Xóa OCR jobs...")
            cursor.execute("DELETE FROM ocr_jobs")
            print(f"   Đã xóa {cursor.rowcount} OCR jobs")

            # 2. Xóa tất cả invoices (đây là test data)
            print("📄 Xóa invoices...")
            cursor.execute("DELETE FROM invoices")
            print(f"   Đã xóa {cursor.rowcount} invoices")

            # 3. Xóa chat history (nếu có)
            print("💬 Xóa chat history...")
            cursor.execute("DELETE FROM chat_history")
            print(f"   Đã xóa {cursor.rowcount} chat records")

            # 4. Xóa user corrections (test data)
            print("🔧 Xóa user corrections...")
            cursor.execute("DELETE FROM user_corrections")
            print(f"   Đã xóa {cursor.rowcount} corrections")

            # 5. Xóa sentiment analysis (test data)
            print("😊 Xóa sentiment analysis...")
            cursor.execute("DELETE FROM sentiment_analysis")
            print(f"   Đã xóa {cursor.rowcount} sentiment records")

            # 6. Xóa OCR notifications (test data)
            print("🔔 Xóa OCR notifications...")
            cursor.execute("DELETE FROM ocr_notifications")
            print(f"   Đã xóa {cursor.rowcount} notifications")

            # 7. Xóa user sessions (test data)
            print("🔑 Xóa user sessions...")
            cursor.execute("DELETE FROM user_sessions")
            print(f"   Đã xóa {cursor.rowcount} sessions")

            # ⚠️ CẨN THẬN: Không xóa users - có thể có user thật
            print("⚠️  Bỏ qua bảng users (có thể chứa user thật)")

            # Commit tất cả thay đổi
            conn.commit()
            print("✅ Đã commit tất cả thay đổi")

        # 8. Xóa file uploads test (nếu có)
        uploads_dir = os.path.join(os.path.dirname(__file__), "..", "uploads")
        if os.path.exists(uploads_dir):
            print("📁 Xóa file uploads test...")
            deleted_files = 0
            for filename in os.listdir(uploads_dir):
                if filename.startswith(("test_", "mock_", "sample_")) or "_test_" in filename:
                    file_path = os.path.join(uploads_dir, filename)
                    try:
                        os.remove(file_path)
                        deleted_files += 1
                        print(f"   Đã xóa: {filename}")
                    except Exception as e:
                        print(f"   Lỗi xóa {filename}: {e}")

            print(f"   Đã xóa {deleted_files} file test")

        # 9. Xóa file temp exports (nếu có)
        temp_dir = os.path.join(os.path.dirname(__file__), "temp_exports")
        if os.path.exists(temp_dir):
            print("📊 Xóa file temp exports...")
            deleted_exports = 0
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                try:
                    os.remove(file_path)
                    deleted_exports += 1
                except Exception as e:
                    print(f"   Lỗi xóa {filename}: {e}")

            print(f"   Đã xóa {deleted_exports} file export temp")

        print("✅ Hoàn thành xóa dữ liệu mock!")
        return True

    except Exception as e:
        print(f"❌ Lỗi khi xóa dữ liệu: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def show_remaining_data():
    """Hiển thị dữ liệu còn lại sau khi xóa"""

    print("\n📊 Dữ liệu còn lại trong database:")

    db_tools = get_database_tools()
    conn = db_tools.connect()

    if not conn:
        print("❌ Không thể kết nối database")
        return

    try:
        with conn.cursor() as cursor:
            # Get all table names
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;")
            tables = cursor.fetchall()

            for table in tables:
                table_name = table['table_name']

                # Count records
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count_result = cursor.fetchone()
                if count_result:
                    count = count_result['count'] if isinstance(count_result, dict) else count_result[0]
                    print(f"  {table_name}: {count} bản ghi")

    except Exception as e:
        print(f"❌ Lỗi khi kiểm tra dữ liệu: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("🗑️ Script xóa dữ liệu mock trong Invoice Management System")
    print("=" * 60)

    # Xác nhận trước khi xóa
    confirm = input("⚠️  Bạn có chắc muốn xóa TẤT CẢ dữ liệu mock? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("❌ Đã hủy thao tác xóa dữ liệu")
        sys.exit(0)

    # Thực hiện xóa
    success = clear_mock_data()

    if success:
        # Hiển thị kết quả
        show_remaining_data()

        print("\n🎉 Hoàn thành!")
        print("💡 Lưu ý: Bảng 'users' không được xóa để tránh mất user thật")
        print("   Nếu muốn xóa users, hãy làm thủ công hoặc sửa script")
    else:
        print("\n❌ Có lỗi xảy ra, vui lòng kiểm tra lại")
        sys.exit(1)