#!/usr/bin/env python3
"""
Script dọn dẹp file test và temp trong hệ thống
"""
import os
import glob
from datetime import datetime, timedelta

def cleanup_test_files():
    """Dọn dẹp file test và temp"""

    print('🧹 Dọn dẹp file test và temp...')

    # Pattern file cần xóa
    patterns = [
        '**/test_*.png', '**/test_*.jpg', '**/test_*.jpeg',
        '**/mock_*.png', '**/mock_*.jpg', '**/mock_*.jpeg',
        '**/sample_*.png', '**/sample_*.jpg', '**/sample_*.jpeg',
        '**/temp_*.xlsx', '**/temp_*.csv', '**/temp_*.pdf',
        'backend/uploads/simple_test.png',
        'backend/uploads/test_invoice_ocr.png'
    ]

    deleted_count = 0

    for pattern in patterns:
        for file_path in glob.glob(pattern, recursive=True):
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print('✅ Đã xóa: {}'.format(file_path))
                    deleted_count += 1
                except Exception as e:
                    print('❌ Lỗi xóa {}: {}'.format(file_path, e))

    # Xóa file temp cũ hơn 1 giờ
    temp_dirs = ['backend/temp_exports', 'temp_exports']
    for temp_dir in temp_dirs:
        if os.path.exists(temp_dir):
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                try:
                    # Kiểm tra thời gian tạo file
                    file_time = os.path.getctime(file_path)
                    file_age = datetime.now() - datetime.fromtimestamp(file_time)

                    # Xóa file cũ hơn 1 giờ
                    if file_age > timedelta(hours=1):
                        os.remove(file_path)
                        print('✅ Đã xóa file temp cũ: {}'.format(filename))
                        deleted_count += 1
                except Exception as e:
                    print('❌ Lỗi xóa {}: {}'.format(file_path, e))

    print()
    print('🎉 Đã xóa tổng cộng {} file'.format(deleted_count))
    return deleted_count

if __name__ == '__main__':
    cleanup_test_files()