#!/usr/bin/env python3
"""
Personalization Script for AI Invoice Assistant
Cá nhân hóa hệ thống cho người dùng cá nhân
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PersonalizationManager:
    """Quản lý cá nhân hóa hệ thống cho người dùng cá nhân"""

    def __init__(self, config_file: str = ".env"):
        self.config_file = config_file
        self.workspace_root = Path(__file__).parent
        self.backend_dir = self.workspace_root / "backend"
        self.frontend_dir = self.workspace_root / "frontend"

        # Load current config
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Load current configuration"""
        config = {}
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            config[key.strip()] = value.strip()
        return config

    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            f.write("# AI Invoice Assistant - Personal Configuration\n")
            f.write("# Cá nhân hóa cho người dùng cá nhân\n\n")

            for key, value in self.config.items():
                f.write(f"{key}={value}\n")

        logger.info(f"Configuration saved to {self.config_file}")

    def get_user_preferences(self) -> Dict[str, Any]:
        """Get current user preferences from database"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return {}

            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Check if user_preferences table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'user_preferences'
                );
            """)

            if not cursor.fetchone()['exists']:
                logger.info("user_preferences table does not exist")
                return {}

            # Get preferences for user (assuming user_id = 1 for personal use)
            cursor.execute("""
                SELECT * FROM user_preferences WHERE user_id = 1;
            """)

            result = cursor.fetchone()
            conn.close()

            return dict(result) if result else {}

        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return {}

    def update_user_preferences(self, preferences: Dict[str, Any]) -> bool:
        """Update user preferences in database"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return False

            cursor = conn.cursor()

            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id INTEGER PRIMARY KEY,
                    theme VARCHAR(50) DEFAULT 'light',
                    language VARCHAR(10) DEFAULT 'vi',
                    currency VARCHAR(10) DEFAULT 'VND',
                    date_format VARCHAR(20) DEFAULT 'DD/MM/YYYY',
                    export_format VARCHAR(20) DEFAULT 'excel',
                    notifications_enabled BOOLEAN DEFAULT true,
                    auto_backup BOOLEAN DEFAULT false,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Insert or update preferences
            cursor.execute("""
                INSERT INTO user_preferences (
                    user_id, theme, language, currency, date_format,
                    export_format, notifications_enabled, auto_backup, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (user_id) DO UPDATE SET
                    theme = EXCLUDED.theme,
                    language = EXCLUDED.language,
                    currency = EXCLUDED.currency,
                    date_format = EXCLUDED.date_format,
                    export_format = EXCLUDED.export_format,
                    notifications_enabled = EXCLUDED.notifications_enabled,
                    auto_backup = EXCLUDED.auto_backup,
                    updated_at = CURRENT_TIMESTAMP;
            """, (
                preferences.get('user_id', 1),
                preferences.get('theme', 'light'),
                preferences.get('language', 'vi'),
                preferences.get('currency', 'VND'),
                preferences.get('date_format', 'DD/MM/YYYY'),
                preferences.get('export_format', 'excel'),
                preferences.get('notifications_enabled', True),
                preferences.get('auto_backup', False)
            ))

            conn.commit()
            conn.close()

            logger.info("User preferences updated successfully")
            return True

        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
            return False

    def personalize_system_prompts(self):
        """Cá nhân hóa system prompts cho người dùng cá nhân"""
        prompt_file = self.backend_dir / "handlers" / "groq_chat_handler.py"

        if not prompt_file.exists():
            logger.warning(f"Prompt file not found: {prompt_file}")
            return

        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Update system prompt for personal use
            old_prompt = """Bạn là trợ lý AI thông minh cho hệ thống quản lý hóa đơn.
Hệ thống này giúp người dùng tải lên hình ảnh hóa đơn và trích xuất thông tin tự động."""

            new_prompt = """Bạn là trợ lý AI cá nhân thông minh cho hệ thống quản lý hóa đơn.
Bạn giúp tôi quản lý và phân tích các hóa đơn cá nhân một cách hiệu quả.
Hỗ trợ trích xuất thông tin từ hình ảnh hóa đơn, xuất báo cáo Excel, và trả lời câu hỏi về tài chính cá nhân."""

            if old_prompt in content:
                content = content.replace(old_prompt, new_prompt)
                logger.info("System prompt updated for personal use")

            # Update export tool description
            old_export_desc = "Xuất dữ liệu hóa đơn ra file Excel"
            new_export_desc = "Xuất báo cáo tài chính cá nhân ra file Excel với bộ lọc theo ngày và loại hóa đơn"

            if old_export_desc in content:
                content = content.replace(old_export_desc, new_export_desc)
                logger.info("Export tool description updated")

            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info("System prompts personalized successfully")

        except Exception as e:
            logger.error(f"Error personalizing system prompts: {e}")

    def personalize_frontend(self):
        """Cá nhân hóa giao diện frontend"""
        # Update main title
        index_file = self.frontend_dir / "index.html"
        if index_file.exists():
            try:
                with open(index_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Update title
                if "<title>AI Invoice Assistant</title>" in content:
                    content = content.replace(
                        "<title>AI Invoice Assistant</title>",
                        "<title>Trợ Lý Hóa Đơn Cá Nhân</title>"
                    )

                # Update main heading
                if "AI Invoice Assistant" in content:
                    content = content.replace(
                        "AI Invoice Assistant",
                        "Trợ Lý Hóa Đơn Cá Nhân"
                    )

                with open(index_file, 'w', encoding='utf-8') as f:
                    f.write(content)

                logger.info("Frontend title updated for personal use")

            except Exception as e:
                logger.error(f"Error personalizing frontend: {e}")

        # Update package.json description
        package_file = self.frontend_dir / "package.json"
        if package_file.exists():
            try:
                with open(package_file, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)

                package_data["description"] = "Giao diện web cho trợ lý hóa đơn cá nhân"

                with open(package_file, 'w', encoding='utf-8') as f:
                    json.dump(package_data, f, indent=2, ensure_ascii=False)

                logger.info("Package description updated")

            except Exception as e:
                logger.error(f"Error updating package.json: {e}")

    def personalize_config(self):
        """Cá nhân hóa cấu hình hệ thống"""
        # Update environment variables for personal use
        personal_config = {
            "SYSTEM_NAME": "Trợ Lý Hóa Đơn Cá Nhân",
            "SYSTEM_DESCRIPTION": "Hệ thống quản lý hóa đơn cá nhân với AI",
            "DEFAULT_LANGUAGE": "vi",
            "DEFAULT_CURRENCY": "VND",
            "DEFAULT_THEME": "light",
            "PERSONAL_MODE": "true",
            "COMPANY_MODE": "false"
        }

        # Update config
        self.config.update(personal_config)
        self.save_config()

        logger.info("Configuration personalized for personal use")

    def create_personal_folders(self):
        """Tạo các thư mục cá nhân"""
        personal_dirs = [
            "personal_data",
            "personal_exports",
            "personal_backups",
            "personal_config"
        ]

        for dir_name in personal_dirs:
            dir_path = self.workspace_root / dir_name
            dir_path.mkdir(exist_ok=True)
            logger.info(f"Created personal directory: {dir_name}")

    def get_db_connection(self):
        """Get database connection"""
        try:
            db_config = {
                'host': self.config.get('DB_HOST', 'localhost'),
                'port': int(self.config.get('DB_PORT', 5432)),
                'database': self.config.get('DB_NAME', 'invoice_db'),
                'user': self.config.get('DB_USER', 'postgres'),
                'password': self.config.get('DB_PASSWORD', 'password')
            }

            conn = psycopg2.connect(**db_config)
            return conn

        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return None

    def run_personalization(self):
        """Chạy toàn bộ quá trình cá nhân hóa"""
        logger.info("Starting personalization for personal use...")

        try:
            # 1. Cá nhân hóa cấu hình
            self.personalize_config()

            # 2. Cá nhân hóa system prompts
            self.personalize_system_prompts()

            # 3. Cá nhân hóa frontend
            self.personalize_frontend()

            # 4. Tạo thư mục cá nhân
            self.create_personal_folders()

            # 5. Thiết lập user preferences mặc định
            default_prefs = {
                'user_id': 1,
                'theme': 'light',
                'language': 'vi',
                'currency': 'VND',
                'date_format': 'DD/MM/YYYY',
                'export_format': 'excel',
                'notifications_enabled': True,
                'auto_backup': False
            }

            self.update_user_preferences(default_prefs)

            logger.info("Personalization completed successfully!")
            logger.info("Hệ thống đã được cá nhân hóa cho người dùng cá nhân")

            return True

        except Exception as e:
            logger.error(f"Personalization failed: {e}")
            return False

    def show_current_personalization(self):
        """Hiển thị trạng thái cá nhân hóa hiện tại"""
        print("\n=== TRẠNG THÁI CÁ NHÂN HÓA HIỆN TẠI ===")

        # Config
        print(f"System Name: {self.config.get('SYSTEM_NAME', 'Not set')}")
        print(f"Personal Mode: {self.config.get('PERSONAL_MODE', 'false')}")
        print(f"Language: {self.config.get('DEFAULT_LANGUAGE', 'Not set')}")
        print(f"Currency: {self.config.get('DEFAULT_CURRENCY', 'Not set')}")

        # User preferences
        prefs = self.get_user_preferences()
        if prefs:
            print(f"\nUser Preferences:")
            for key, value in prefs.items():
                if key != 'user_id':
                    print(f"  {key}: {value}")
        else:
            print("\nNo user preferences found")

        # Personal folders
        personal_dirs = ["personal_data", "personal_exports", "personal_backups", "personal_config"]
        existing_dirs = [d for d in personal_dirs if (self.workspace_root / d).exists()]
        print(f"\nPersonal Directories: {len(existing_dirs)}/{len(personal_dirs)} created")
        for d in existing_dirs:
            print(f"  ✓ {d}")

def main():
    """Main function"""
    print("🚀 AI Invoice Assistant - Personalization Tool")
    print("Công cụ cá nhân hóa cho người dùng cá nhân")
    print("=" * 50)

    manager = PersonalizationManager()

    while True:
        print("\nChọn tùy chọn:")
        print("1. Cá nhân hóa hệ thống")
        print("2. Hiển thị trạng thái cá nhân hóa hiện tại")
        print("3. Cập nhật sở thích cá nhân")
        print("4. Thoát")

        choice = input("\nNhập lựa chọn (1-4): ").strip()

        if choice == "1":
            print("\nĐang cá nhân hóa hệ thống...")
            success = manager.run_personalization()
            if success:
                print("✅ Cá nhân hóa thành công!")
            else:
                print("❌ Cá nhân hóa thất bại!")

        elif choice == "2":
            manager.show_current_personalization()

        elif choice == "3":
            print("\nCập nhật sở thích cá nhân:")
            prefs = {}

            print("Theme (light/dark): ", end="")
            theme = input().strip() or "light"
            prefs['theme'] = theme

            print("Language (vi/en): ", end="")
            lang = input().strip() or "vi"
            prefs['language'] = lang

            print("Currency (VND/USD): ", end="")
            currency = input().strip() or "VND"
            prefs['currency'] = currency

            print("Export format (excel/pdf/csv): ", end="")
            export_format = input().strip() or "excel"
            prefs['export_format'] = export_format

            print("Enable notifications (y/n): ", end="")
            notifications = input().strip().lower() in ['y', 'yes', 'true']
            prefs['notifications_enabled'] = notifications

            success = manager.update_user_preferences(prefs)
            if success:
                print("✅ Sở thích cá nhân đã được cập nhật!")
            else:
                print("❌ Cập nhật sở thích thất bại!")

        elif choice == "4":
            print("Tạm biệt! 👋")
            break

        else:
            print("❌ Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    main()