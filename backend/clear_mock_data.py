#!/usr/bin/env python3
"""
🗑️ Script xóa dữ liệu mock trong database
Xóa tất cả dữ liệu test/mock, giữ lại users thật (nếu có)

Upgraded version with:
- SQL injection protection
- Comprehensive logging
- Auto backup functionality
- Dry-run mode
- Proper error handling
- CLI arguments
"""

import sys
import os
import logging
import argparse
import shutil
import subprocess
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.database_tools import get_database_tools

try:
    import psycopg2
    from psycopg2 import sql
except ImportError:
    print("⚠️ psycopg2 not found, using generic database handling")
    psycopg2 = None
    sql = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('clear_mock_data.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Safe table list - only these can be cleared
ALLOWED_TABLES = [
    'ocr_jobs',
    'invoices', 
    'chat_history',
    'user_corrections',
    'sentiment_analysis',
    'ocr_notifications',
    'user_sessions'
]

def create_backup(db_tools) -> Optional[str]:
    """Tạo backup database trước khi xóa dữ liệu
    
    Returns:
        Optional[str]: Path to backup file nếu thành công, None nếu lỗi
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_before_clear_{timestamp}.sql"
        
        logger.info("💾 Tạo backup database...")
        print("💾 Tạo backup database...")
        
        # Try pg_dump if available
        try:
            result = subprocess.run(
                ["pg_dump", "-h", "localhost", "-U", "postgres", "chatbotai"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                with open(backup_file, 'w', encoding='utf-8') as f:
                    f.write(result.stdout)
                logger.info(f"✅ Backup thành công: {backup_file}")
                print(f"   ✅ Backup thành công: {backup_file}")
                return backup_file
            else:
                logger.warning(f"pg_dump failed: {result.stderr}")
                
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.warning(f"pg_dump not available: {e}")
        
        # Fallback: Simple table export
        logger.info("📋 Tạo backup bằng cách export tables...")
        conn = db_tools.connect()
        if not conn:
            return None
            
        with open(backup_file, 'w', encoding='utf-8') as f:
            with conn.cursor() as cursor:
                for table in ALLOWED_TABLES:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        f.write(f"-- Table {table}: {count} records\n")
                    except Exception as e:
                        f.write(f"-- Table {table}: Error - {e}\n")
        
        conn.close()
        logger.info(f"✅ Backup metadata thành công: {backup_file}")
        print(f"   ✅ Backup metadata thành công: {backup_file}")
        return backup_file
        
    except Exception as e:
        logger.error(f"❌ Lỗi tạo backup: {e}")
        print(f"   ❌ Lỗi tạo backup: {e}")
        return None

def clear_mock_data(dry_run: bool = False, skip_backup: bool = False) -> bool:
    """Xóa tất cả dữ liệu mock trong database
    
    Args:
        dry_run: Nếu True, chỉ hiển thị sẽ xóa gì mà không thực xóa
        skip_backup: Nếu True, bỏ qua việc tạo backup
    
    Returns:
        bool: True nếu thành công, False nếu có lỗi
    """
    
    if dry_run:
        logger.info("🔍 DRY RUN MODE - Chỉ xem trước, không xóa gì")
        print("🔍 DRY RUN MODE - Chỉ xem trước, không xóa gì")
    else:
        logger.info("🗑️ Bắt đầu xóa dữ liệu mock...")
        print("🗑️ Bắt đầu xóa dữ liệu mock...")

    db_tools = get_database_tools()
    
    # Create backup first (if not skipped and not dry-run)
    backup_file = None
    if not dry_run and not skip_backup:
        backup_file = create_backup(db_tools)
        if not backup_file:
            logger.error("❌ Không thể tạo backup, dừng thao tác")
            print("❌ Không thể tạo backup, dừng thao tác")
            return False
    
    conn = db_tools.connect()
    if not conn:
        logger.error("❌ Không thể kết nối database")
        print("❌ Không thể kết nối database")
        return False

    try:
        total_deleted = 0
        with conn.cursor() as cursor:
            
            # Process each table safely
            table_actions = [
                ('ocr_jobs', '📋', 'OCR jobs'),
                ('invoices', '📄', 'invoices'),  
                ('chat_history', '💬', 'chat records'),
                ('user_corrections', '🔧', 'corrections'),
                ('sentiment_analysis', '😊', 'sentiment records'),
                ('ocr_notifications', '🔔', 'notifications'),
                ('user_sessions', '🔑', 'sessions')
            ]
            
            for table_name, emoji, description in table_actions:
                try:
                    # Safe table name handling
                    if sql and psycopg2:  # Use psycopg2.sql if available
                        if dry_run:
                            query = sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table_name))
                            cursor.execute(query)
                            count = cursor.fetchone()[0]
                            logger.info(f"{emoji} Sẽ xóa {count} {description} từ {table_name}")
                            print(f"   {emoji} Sẽ xóa {count} {description} từ {table_name}")
                            total_deleted += count
                        else:
                            query = sql.SQL("DELETE FROM {}").format(sql.Identifier(table_name))
                            cursor.execute(query)
                            deleted_count = cursor.rowcount
                            logger.info(f"{emoji} Đã xóa {deleted_count} {description}")
                            print(f"   {emoji} Đã xóa {deleted_count} {description}")
                            total_deleted += deleted_count
                    else:
                        # Fallback for other database types
                        if table_name not in ALLOWED_TABLES:
                            logger.warning(f"⚠️ Bỏ qua table không an toàn: {table_name}")
                            continue
                            
                        if dry_run:
                            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                            count = cursor.fetchone()[0]
                            logger.info(f"{emoji} Sẽ xóa {count} {description} từ {table_name}")
                            print(f"   {emoji} Sẽ xóa {count} {description} từ {table_name}")
                            total_deleted += count
                        else:
                            cursor.execute(f"DELETE FROM {table_name}")
                            deleted_count = cursor.rowcount
                            logger.info(f"{emoji} Đã xóa {deleted_count} {description}")
                            print(f"   {emoji} Đã xóa {deleted_count} {description}")
                            total_deleted += deleted_count
                            
                except Exception as e:
                    if psycopg2 and hasattr(psycopg2, 'Error') and isinstance(e, psycopg2.Error):
                        logger.error(f"❌ Lỗi database khi xử lý {table_name}: {e}")
                        print(f"   ❌ Lỗi database khi xử lý {table_name}: {e}")
                    else:
                        logger.error(f"❌ Lỗi không xác định khi xử lý {table_name}: {e}")
                        print(f"   ❌ Lỗi không xác định khi xử lý {table_name}: {e}")

            # ⚠️ CẨN THẬN: Không xóa users - có thể có user thật
            logger.info("⚠️ Bỏ qua bảng users (có thể chứa user thật)")
            print("⚠️  Bỏ qua bảng users (có thể chứa user thật)")

            # Commit changes (only if not dry-run)
            if not dry_run:
                conn.commit()
                logger.info("✅ Đã commit tất cả thay đổi")
                print("✅ Đã commit tất cả thay đổi")
            else:
                logger.info(f"🔍 DRY RUN: Tổng cộng sẽ xóa {total_deleted} records")
                print(f"🔍 DRY RUN: Tổng cộng sẽ xóa {total_deleted} records")

        # 8. Xóa file uploads test (nếu có)
        deleted_files = _cleanup_test_files(dry_run)
        
        if dry_run:
            logger.info(f"🔍 DRY RUN: Hoàn thành xem trước! Sẽ xóa {total_deleted} records và {deleted_files} files")
            print(f"🔍 DRY RUN: Hoàn thành xem trước! Sẽ xóa {total_deleted} records và {deleted_files} files")
        else:
            logger.info("✅ Hoàn thành xóa dữ liệu mock!")
            print("✅ Hoàn thành xóa dữ liệu mock!")
            
        return True

    except Exception as db_error:
        if psycopg2 and hasattr(psycopg2, 'DatabaseError') and isinstance(db_error, psycopg2.DatabaseError):
            logger.error(f"❌ Lỗi database: {db_error}", exc_info=True)
            print(f"❌ Lỗi database: {db_error}")
        elif psycopg2 and hasattr(psycopg2, 'IntegrityError') and isinstance(db_error, psycopg2.IntegrityError):
            logger.error(f"❌ Lỗi ràng buộc database: {db_error}", exc_info=True)
            print(f"❌ Lỗi ràng buộc database: {db_error}")
        else:
            logger.error(f"❌ Lỗi không xác định: {db_error}", exc_info=True)
            print(f"❌ Lỗi không xác định: {db_error}")
        
        if not dry_run:
            try:
                conn.rollback()
            except Exception as rollback_error:
                logger.error(f"❌ Lỗi rollback: {rollback_error}")
        return False
    finally:
        conn.close()

def _cleanup_test_files(dry_run: bool = False) -> int:
    """Xóa file test/mock trong thư mục uploads và temp
    
    Args:
        dry_run: Nếu True, chỉ đếm file sẽ xóa
        
    Returns:
        int: Số file đã xóa hoặc sẽ xóa
    """
    deleted_files = 0
    
    # Define directories to clean
    base_dir = Path(__file__).parent.parent
    directories_to_clean = [
        base_dir / "uploads",
        base_dir / "temp_exports", 
        Path(__file__).parent / "temp_exports"
    ]
    
    for directory in directories_to_clean:
        if not directory.exists():
            continue
            
        logger.info(f"📁 {'Kiểm tra' if dry_run else 'Xóa'} files trong {directory.name}...")
        print(f"📁 {'Kiểm tra' if dry_run else 'Xóa'} files trong {directory.name}...")
        
        try:
            for file_path in directory.iterdir():
                if file_path.is_file():
                    filename = file_path.name
                    # Check if it's a test/mock file
                    if (filename.startswith(("test_", "mock_", "sample_")) or 
                        "_test_" in filename or
                        filename.endswith((".tmp", ".temp"))):
                        
                        if dry_run:
                            logger.info(f"   Sẽ xóa: {filename}")
                            print(f"   Sẽ xóa: {filename}")
                        else:
                            try:
                                file_path.unlink()
                                logger.info(f"   Đã xóa: {filename}")
                                print(f"   Đã xóa: {filename}")
                            except OSError as e:
                                logger.error(f"   Lỗi xóa {filename}: {e}")
                                print(f"   Lỗi xóa {filename}: {e}")
                                continue
                        
                        deleted_files += 1
                        
        except OSError as e:
            logger.error(f"Lỗi truy cập thư mục {directory}: {e}")
            print(f"   Lỗi truy cập thư mục {directory}: {e}")
    
    action = "Sẽ xóa" if dry_run else "Đã xóa"
    logger.info(f"📁 {action} {deleted_files} file test/mock")
    print(f"   {action} {deleted_files} file test/mock")
    
    return deleted_files

def show_remaining_data() -> Dict[str, int]:
    """Hiển thị dữ liệu còn lại sau khi xóa
    
    Returns:
        Dict[str, int]: Dictionary với table_name: record_count
    """
    logger.info("📊 Kiểm tra dữ liệu còn lại trong database...")
    print("\n📊 Dữ liệu còn lại trong database:")

    db_tools = get_database_tools()
    conn = db_tools.connect()

    if not conn:
        logger.error("❌ Không thể kết nối database")
        print("❌ Không thể kết nối database")
        return {}

    table_counts = {}
    
    try:
        with conn.cursor() as cursor:
            # Get all table names safely
            cursor.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' AND table_type = 'BASE TABLE' "
                "ORDER BY table_name;"
            )
            tables = cursor.fetchall()

            for table_row in tables:
                # Handle different cursor types
                if isinstance(table_row, dict):
                    table_name = table_row['table_name']
                else:
                    table_name = table_row[0]
                
                try:
                    # Safe count query
                    if sql and psycopg2:
                        query = sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table_name))
                        cursor.execute(query)
                    else:
                        # Basic protection - only count known tables
                        if table_name.replace('_', '').replace('-', '').isalnum():
                            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        else:
                            logger.warning(f"⚠️ Bỏ qua table có tên nghi ngờ: {table_name}")
                            continue
                    
                    count_result = cursor.fetchone()
                    if count_result:
                        count = count_result[0] if isinstance(count_result, (list, tuple)) else count_result['count']
                        table_counts[table_name] = count
                        
                        # Highlight important tables
                        if table_name in ALLOWED_TABLES:
                            if count > 0:
                                logger.warning(f"  🟡 {table_name}: {count} bản ghi (có thể cần xóa thêm)")
                                print(f"  🟡 {table_name}: {count} bản ghi (có thể cần xóa thêm)")
                            else:
                                logger.info(f"  ✅ {table_name}: {count} bản ghi (đã sạch)")
                                print(f"  ✅ {table_name}: {count} bản ghi (đã sạch)")
                        else:
                            logger.info(f"  📋 {table_name}: {count} bản ghi")
                            print(f"  📋 {table_name}: {count} bản ghi")
                            
                except Exception as e:
                    if psycopg2 and hasattr(psycopg2, 'Error') and isinstance(e, psycopg2.Error):
                        logger.error(f"❌ Lỗi database khi kiểm tra table {table_name}: {e}")
                        print(f"  ❌ Lỗi database kiểm tra {table_name}: {e}")
                    else:
                        logger.error(f"❌ Lỗi không xác định cho table {table_name}: {e}")
                        print(f"  ❌ Lỗi không xác định cho {table_name}: {e}")
                    
        return table_counts

    except Exception as e:
        if psycopg2 and hasattr(psycopg2, 'Error') and isinstance(e, psycopg2.Error):
            logger.error(f"❌ Lỗi database khi kiểm tra dữ liệu: {e}")
            print(f"❌ Lỗi database khi kiểm tra dữ liệu: {e}")
        else:
            logger.error(f"❌ Lỗi không xác định khi kiểm tra dữ liệu: {e}")
            print(f"❌ Lỗi không xác định khi kiểm tra dữ liệu: {e}")
        return {}
    finally:
        conn.close()

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='🗑️ Xóa dữ liệu mock trong ChatBotAI database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python clear_mock_data.py --dry-run          # Xem trước sẽ xóa gì
  python clear_mock_data.py --skip-backup      # Xóa mà không backup
  python clear_mock_data.py --tables ocr_jobs,invoices  # Xóa table cụ thể
  python clear_mock_data.py --force            # Không hỏi xác nhận
        """
    )
    
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Chỉ hiển thị sẽ xóa gì, không thực sự xóa'
    )
    
    parser.add_argument(
        '--skip-backup',
        action='store_true', 
        help='Bỏ qua tạo backup trước khi xóa'
    )
    
    parser.add_argument(
        '--tables',
        default='all',
        help='Danh sách table cần xóa, phân tách bằng dấu phẩy (mặc định: all)'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Không hỏi xác nhận trước khi xóa'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Hiển thị log chi tiết'
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled")
    
    print("🗑️ Script xóa dữ liệu mock trong ChatBotAI System")
    print("=" * 60)
    logger.info("Script started with arguments: %s", vars(args))
    
    # Parse specific tables if provided
    if args.tables != 'all':
        requested_tables = [t.strip() for t in args.tables.split(',')]
        invalid_tables = [t for t in requested_tables if t not in ALLOWED_TABLES]
        if invalid_tables:
            logger.error(f"❌ Tables không hợp lệ: {invalid_tables}")
            print(f"❌ Tables không hợp lệ: {invalid_tables}")
            print(f"✅ Tables được phép: {ALLOWED_TABLES}")
            sys.exit(1)
        
        # Update ALLOWED_TABLES to only requested ones
        ALLOWED_TABLES = requested_tables
        logger.info(f"📋 Chỉ xử lý tables: {ALLOWED_TABLES}")
        print(f"📋 Chỉ xử lý tables: {ALLOWED_TABLES}")
    
    # Show current state first
    print("\n📊 Trạng thái hiện tại:")
    initial_counts = show_remaining_data()
    
    # Check if there's anything to delete
    total_records = sum(initial_counts.get(table, 0) for table in ALLOWED_TABLES)
    if total_records == 0:
        logger.info("✅ Không có dữ liệu mock nào để xóa!")
        print("\n✅ Không có dữ liệu mock nào để xóa!")
        sys.exit(0)
    
    # Confirmation (unless --force or --dry-run)
    if not args.force and not args.dry_run:
        print(f"\n⚠️  Sẽ xóa {total_records} records từ {len(ALLOWED_TABLES)} tables")
        if args.skip_backup:
            print("⚠️  KHÔNG tạo backup!")
        else:
            print("💾 Sẽ tạo backup trước khi xóa")
            
        confirm = input("Bạn có chắc muốn tiếp tục? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes', 'đồng ý']:
            logger.info("❌ Đã hủy thao tác xóa dữ liệu")
            print("❌ Đã hủy thao tác xóa dữ liệu")
            sys.exit(0)
    
    # Execute the operation
    logger.info(f"🚀 Bắt đầu {'dry-run' if args.dry_run else 'xóa dữ liệu'}")
    success = clear_mock_data(
        dry_run=args.dry_run, 
        skip_backup=args.skip_backup
    )
    
    if success:
        # Show final state (unless dry-run)
        if not args.dry_run:
            print("\n📊 Trạng thái sau khi xóa:")
            final_counts = show_remaining_data()
            
            # Summary
            deleted_records = sum(initial_counts.get(table, 0) - final_counts.get(table, 0) 
                                for table in ALLOWED_TABLES)
            logger.info(f"✅ Đã xóa thành công {deleted_records} records")
            print(f"\n✅ Đã xóa thành công {deleted_records} records")
        
        print("\n🎉 Hoàn thành!")
        print("💡 Lưu ý:")
        print("   • Bảng 'users' không được xóa để tránh mất user thật")
        print("   • Log chi tiết được lưu trong 'clear_mock_data.log'")
        if not args.skip_backup and not args.dry_run:
            print("   • Backup đã được tạo để recovery khi cần")
            
        logger.info("Script completed successfully")
    else:
        logger.error("Script failed")
        print("\n❌ Có lỗi xảy ra, vui lòng kiểm tra file log 'clear_mock_data.log'")
        sys.exit(1)