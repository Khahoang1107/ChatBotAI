"""
Database utilities for the Invoice Management API
"""

from flask import current_app
from models import db, User, InvoiceTemplate
from werkzeug.security import generate_password_hash
import json


def init_database():
    """Initialize database with tables and default data"""
    try:
        # Create all tables
        db.create_all()
        current_app.logger.info("Database tables created successfully")
        
        # Create default templates if they don't exist
        create_default_templates()
        
        # Create admin user if it doesn't exist
        create_admin_user()
        
        return True
    except Exception as e:
        current_app.logger.error(f"Database initialization failed: {str(e)}")
        return False


def create_default_templates():
    """Create default invoice templates"""
    
    # Vietnamese Standard Invoice Template
    vn_template = InvoiceTemplate.query.filter_by(
        name="Vietnamese Standard Invoice",
        is_default=True
    ).first()
    
    if not vn_template:
        field_mappings = {
            'invoice_number': {'required': True, 'type': 'string', 'patterns': ['Số HĐ', 'Invoice No']},
            'company_name': {'required': True, 'type': 'string', 'patterns': ['Đơn vị bán hàng', 'Seller']},
            'company_address': {'required': False, 'type': 'string', 'patterns': ['Địa chỉ', 'Address']},
            'company_tax_id': {'required': False, 'type': 'string', 'patterns': ['MST', 'Tax ID']},
            'customer_name': {'required': True, 'type': 'string', 'patterns': ['Tên đơn vị', 'Buyer']},
            'customer_address': {'required': False, 'type': 'string', 'patterns': ['Địa chỉ KH', 'Customer Address']},
            'customer_tax_id': {'required': False, 'type': 'string', 'patterns': ['MST KH', 'Customer Tax ID']},
            'invoice_date': {'required': True, 'type': 'date', 'patterns': ['Ngày lập', 'Date']},
            'total_amount': {'required': True, 'type': 'decimal', 'patterns': ['Tổng cộng', 'Total']},
            'tax_amount': {'required': False, 'type': 'decimal', 'patterns': ['Thuế GTGT', 'VAT']},
            'subtotal': {'required': False, 'type': 'decimal', 'patterns': ['Tiền hàng', 'Subtotal']},
            'currency': {'required': False, 'type': 'string', 'default': 'VND'},
            'items': {'required': False, 'type': 'array', 'patterns': ['Diễn giải', 'Description']}
        }
        
        ocr_zones = {
            'header': {'y_start': 0, 'y_end': 0.2, 'fields': ['company_name', 'company_address']},
            'invoice_info': {'y_start': 0.2, 'y_end': 0.4, 'fields': ['invoice_number', 'invoice_date']},
            'customer_info': {'y_start': 0.4, 'y_end': 0.6, 'fields': ['customer_name', 'customer_address']},
            'items': {'y_start': 0.6, 'y_end': 0.85, 'fields': ['items']},
            'totals': {'y_start': 0.85, 'y_end': 1.0, 'fields': ['subtotal', 'tax_amount', 'total_amount']}
        }
        
        vn_template = InvoiceTemplate(
            name="Vietnamese Standard Invoice",
            user_id=None,  # System template
            description="Standard Vietnamese invoice template with VAT",
            is_default=True
        )
        vn_template.set_field_mappings(field_mappings)
        vn_template.set_ocr_zones(ocr_zones)
        
        db.session.add(vn_template)
    
    # English Invoice Template
    en_template = InvoiceTemplate.query.filter_by(
        name="English Standard Invoice",
        is_default=True
    ).first()
    
    if not en_template:
        field_mappings = {
            'invoice_number': {'required': True, 'type': 'string', 'patterns': ['Invoice Number', 'Invoice No']},
            'company_name': {'required': True, 'type': 'string', 'patterns': ['Company', 'From']},
            'company_address': {'required': False, 'type': 'string', 'patterns': ['Address', 'Company Address']},
            'customer_name': {'required': True, 'type': 'string', 'patterns': ['Bill To', 'Customer', 'To']},
            'customer_address': {'required': False, 'type': 'string', 'patterns': ['Billing Address', 'Customer Address']},
            'invoice_date': {'required': True, 'type': 'date', 'patterns': ['Date', 'Invoice Date']},
            'due_date': {'required': False, 'type': 'date', 'patterns': ['Due Date', 'Payment Due']},
            'total_amount': {'required': True, 'type': 'decimal', 'patterns': ['Total', 'Amount Due']},
            'tax_amount': {'required': False, 'type': 'decimal', 'patterns': ['Tax', 'VAT', 'Sales Tax']},
            'subtotal': {'required': False, 'type': 'decimal', 'patterns': ['Subtotal', 'Net Amount']},
            'currency': {'required': False, 'type': 'string', 'default': 'USD'},
            'items': {'required': False, 'type': 'array', 'patterns': ['Description', 'Item']}
        }
        
        ocr_zones = {
            'header': {'y_start': 0, 'y_end': 0.25, 'fields': ['company_name', 'company_address', 'invoice_number']},
            'dates': {'y_start': 0.25, 'y_end': 0.35, 'fields': ['invoice_date', 'due_date']},
            'customer_info': {'y_start': 0.35, 'y_end': 0.5, 'fields': ['customer_name', 'customer_address']},
            'items': {'y_start': 0.5, 'y_end': 0.8, 'fields': ['items']},
            'totals': {'y_start': 0.8, 'y_end': 1.0, 'fields': ['subtotal', 'tax_amount', 'total_amount']}
        }
        
        en_template = InvoiceTemplate(
            name="English Standard Invoice",
            user_id=None,  # System template
            description="Standard English invoice template",
            is_default=True
        )
        en_template.set_field_mappings(field_mappings)
        en_template.set_ocr_zones(ocr_zones)
        
        db.session.add(en_template)
    
    # Simple Receipt Template
    receipt_template = InvoiceTemplate.query.filter_by(
        name="Simple Receipt",
        is_default=True
    ).first()
    
    if not receipt_template:
        field_mappings = {
            'invoice_number': {'required': True, 'type': 'string', 'patterns': ['Receipt', 'No']},
            'company_name': {'required': True, 'type': 'string'},
            'customer_name': {'required': False, 'type': 'string'},
            'invoice_date': {'required': True, 'type': 'date', 'patterns': ['Date']},
            'total_amount': {'required': True, 'type': 'decimal', 'patterns': ['Total', 'Amount']},
            'currency': {'required': False, 'type': 'string', 'default': 'VND'},
            'items': {'required': False, 'type': 'array'}
        }
        
        receipt_template = InvoiceTemplate(
            name="Simple Receipt",
            user_id=None,
            description="Simple receipt template for basic transactions",
            is_default=True
        )
        receipt_template.set_field_mappings(field_mappings)
        
        db.session.add(receipt_template)
    
    try:
        db.session.commit()
        current_app.logger.info("Default templates created successfully")
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to create default templates: {str(e)}")


def create_admin_user():
    """Create default admin user if it doesn't exist"""
    admin_user = User.query.filter_by(username='admin').first()
    
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@invoiceapp.com',
            full_name='Administrator'
        )
        admin_user.set_password('admin123')  # Change this in production!
        
        try:
            db.session.add(admin_user)
            db.session.commit()
            current_app.logger.info("Admin user created successfully")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Failed to create admin user: {str(e)}")


def reset_database():
    """Reset database - DROP ALL TABLES and recreate"""
    try:
        db.drop_all()
        current_app.logger.info("All database tables dropped")
        
        db.create_all()
        current_app.logger.info("Database tables recreated")
        
        create_default_templates()
        create_admin_user()
        
        return True
    except Exception as e:
        current_app.logger.error(f"Database reset failed: {str(e)}")
        return False


def backup_database():
    """Create a backup of the database"""
    # This is a simple implementation for SQLite
    # For production PostgreSQL, use pg_dump
    try:
        import shutil
        from datetime import datetime
        
        if 'sqlite' in current_app.config['SQLALCHEMY_DATABASE_URI']:
            db_path = current_app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            backup_path = f"{db_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            shutil.copy2(db_path, backup_path)
            current_app.logger.info(f"Database backed up to {backup_path}")
            return backup_path
        else:
            current_app.logger.warning("Backup only implemented for SQLite")
            return None
            
    except Exception as e:
        current_app.logger.error(f"Database backup failed: {str(e)}")
        return None


def get_database_stats():
    """Get database statistics"""
    try:
        stats = {
            'users': User.query.count(),
            'templates': InvoiceTemplate.query.count(),
            'default_templates': InvoiceTemplate.query.filter_by(is_default=True).count(),
        }
        
        # Add invoice stats if models are imported
        try:
            from models import Invoice, InvoiceItem, OCRResult
            stats.update({
                'invoices': Invoice.query.count(),
                'invoice_items': InvoiceItem.query.count(),
                'ocr_results': OCRResult.query.count()
            })
        except ImportError:
            pass
        
        return stats
    except Exception as e:
        current_app.logger.error(f"Failed to get database stats: {str(e)}")
        return {}


def validate_database():
    """Validate database integrity"""
    issues = []
    
    try:
        # Check for orphaned records
        from models import Invoice, InvoiceTemplate, OCRResult
        
        # Check for invoices without users
        orphaned_invoices = Invoice.query.outerjoin(User).filter(User.id.is_(None)).count()
        if orphaned_invoices > 0:
            issues.append(f"{orphaned_invoices} invoices without valid users")
        
        # Check for templates without users (excluding defaults)
        orphaned_templates = InvoiceTemplate.query.outerjoin(User).filter(
            User.id.is_(None),
            InvoiceTemplate.is_default == False
        ).count()
        if orphaned_templates > 0:
            issues.append(f"{orphaned_templates} user templates without valid users")
        
        # Check for OCR results without valid invoices
        orphaned_ocr = OCRResult.query.outerjoin(Invoice).filter(
            OCRResult.invoice_id.isnot(None),
            Invoice.id.is_(None)
        ).count()
        if orphaned_ocr > 0:
            issues.append(f"{orphaned_ocr} OCR results with invalid invoice references")
        
        return issues
        
    except Exception as e:
        current_app.logger.error(f"Database validation failed: {str(e)}")
        return [f"Validation error: {str(e)}"]