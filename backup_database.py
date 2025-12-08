#!/usr/bin/env python3
"""
Auto backup database script
Tự động backup database mỗi khi chạy hoặc theo lịch
"""
import os
import shutil
from datetime import datetime
import sys

# Đường dẫn
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'chatbot.db')
BACKUP_DIR = os.path.join(BASE_DIR, 'database_backups')

def create_backup():
    """Tạo backup của database"""
    try:
        # Tạo thư mục backup nếu chưa có
        os.makedirs(BACKUP_DIR, exist_ok=True)
        
        # Kiểm tra database có tồn tại
        if not os.path.exists(DB_PATH):
            print(f"❌ Database không tồn tại: {DB_PATH}")
            return False
        
        # Tạo tên file backup với timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'chatbot_backup_{timestamp}.db'
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        
        # Copy database
        shutil.copy2(DB_PATH, backup_path)
        
        # Lấy kích thước file
        size_kb = os.path.getsize(backup_path) / 1024
        
        print(f"✅ Backup thành công!")
        print(f"   📁 File: {backup_filename}")
        print(f"   💾 Kích thước: {size_kb:.2f} KB")
        print(f"   📂 Thư mục: {BACKUP_DIR}")
        
        # Xóa backup cũ (giữ lại 10 bản gần nhất)
        cleanup_old_backups()
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi backup: {e}")
        return False

def cleanup_old_backups(keep_count=10):
    """Xóa các backup cũ, chỉ giữ lại số lượng backup gần nhất"""
    try:
        # Lấy danh sách tất cả backup files
        backup_files = []
        for filename in os.listdir(BACKUP_DIR):
            if filename.startswith('chatbot_backup_') and filename.endswith('.db'):
                filepath = os.path.join(BACKUP_DIR, filename)
                backup_files.append((filepath, os.path.getmtime(filepath)))
        
        # Sắp xếp theo thời gian (mới nhất trước)
        backup_files.sort(key=lambda x: x[1], reverse=True)
        
        # Xóa các file cũ
        deleted_count = 0
        for filepath, _ in backup_files[keep_count:]:
            os.remove(filepath)
            deleted_count += 1
        
        if deleted_count > 0:
            print(f"   🗑️  Đã xóa {deleted_count} backup cũ")
            
    except Exception as e:
        print(f"⚠️  Không thể xóa backup cũ: {e}")

def restore_backup(backup_filename=None):
    """Khôi phục database từ backup"""
    try:
        if backup_filename is None:
            # Lấy backup mới nhất
            backup_files = []
            for filename in os.listdir(BACKUP_DIR):
                if filename.startswith('chatbot_backup_') and filename.endswith('.db'):
                    filepath = os.path.join(BACKUP_DIR, filename)
                    backup_files.append((filepath, os.path.getmtime(filepath)))
            
            if not backup_files:
                print("❌ Không tìm thấy backup nào!")
                return False
            
            # Sắp xếp và lấy file mới nhất
            backup_files.sort(key=lambda x: x[1], reverse=True)
            backup_path = backup_files[0][0]
            backup_filename = os.path.basename(backup_path)
        else:
            backup_path = os.path.join(BACKUP_DIR, backup_filename)
        
        if not os.path.exists(backup_path):
            print(f"❌ Backup không tồn tại: {backup_filename}")
            return False
        
        # Backup database hiện tại trước khi restore
        if os.path.exists(DB_PATH):
            temp_backup = DB_PATH + '.before_restore'
            shutil.copy2(DB_PATH, temp_backup)
            print(f"   💾 Đã backup database hiện tại: {os.path.basename(temp_backup)}")
        
        # Restore từ backup
        shutil.copy2(backup_path, DB_PATH)
        
        print(f"✅ Khôi phục thành công từ: {backup_filename}")
        return True
        
    except Exception as e:
        print(f"❌ Lỗi khi khôi phục: {e}")
        return False

def list_backups():
    """Liệt kê tất cả các backup"""
    try:
        if not os.path.exists(BACKUP_DIR):
            print("📂 Chưa có backup nào")
            return
        
        backup_files = []
        for filename in os.listdir(BACKUP_DIR):
            if filename.startswith('chatbot_backup_') and filename.endswith('.db'):
                filepath = os.path.join(BACKUP_DIR, filename)
                mtime = os.path.getmtime(filepath)
                size = os.path.getsize(filepath) / 1024
                backup_files.append((filename, mtime, size))
        
        if not backup_files:
            print("📂 Chưa có backup nào")
            return
        
        # Sắp xếp theo thời gian
        backup_files.sort(key=lambda x: x[1], reverse=True)
        
        print(f"\n📋 Danh sách backup ({len(backup_files)} file):")
        print("-" * 70)
        for i, (filename, mtime, size) in enumerate(backup_files, 1):
            dt = datetime.fromtimestamp(mtime)
            print(f"{i:2}. {filename}")
            print(f"    Thời gian: {dt.strftime('%d/%m/%Y %H:%M:%S')}")
            print(f"    Kích thước: {size:.2f} KB")
            print()
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Database backup tool')
    parser.add_argument('action', choices=['backup', 'restore', 'list'], 
                        help='Hành động: backup (tạo backup), restore (khôi phục), list (xem danh sách)')
    parser.add_argument('--file', help='Tên file backup để restore')
    
    args = parser.parse_args()
    
    if args.action == 'backup':
        create_backup()
    elif args.action == 'restore':
        restore_backup(args.file)
    elif args.action == 'list':
        list_backups()
