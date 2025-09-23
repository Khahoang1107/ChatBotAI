from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token
import json

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    invoices = db.relationship('Invoice', backref='user', lazy=True, cascade='all, delete-orphan')
    templates = db.relationship('InvoiceTemplate', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Check password against hash"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def generate_tokens(self):
        """Generate access and refresh tokens"""
        access_token = create_access_token(identity=self.id)
        refresh_token = create_refresh_token(identity=self.id)
        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }


class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Invoice details
    company_name = db.Column(db.String(200))
    company_address = db.Column(db.Text)
    company_tax_id = db.Column(db.String(50))
    company_phone = db.Column(db.String(20))
    company_email = db.Column(db.String(120))
    
    # Customer details
    customer_name = db.Column(db.String(200))
    customer_address = db.Column(db.Text)
    customer_tax_id = db.Column(db.String(50))
    customer_phone = db.Column(db.String(20))
    customer_email = db.Column(db.String(120))
    
    # Invoice financial data
    subtotal = db.Column(db.Numeric(10, 2))
    tax_amount = db.Column(db.Numeric(10, 2))
    total_amount = db.Column(db.Numeric(10, 2))
    currency = db.Column(db.String(3), default='VND')
    
    # Dates
    invoice_date = db.Column(db.Date)
    due_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # File and processing info
    original_file_path = db.Column(db.String(500))
    ocr_confidence = db.Column(db.Float)
    template_id = db.Column(db.Integer, db.ForeignKey('invoice_templates.id'))
    
    # Status
    status = db.Column(db.String(20), default='pending')  # pending, processed, verified, archived
    
    # Relationships
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True, cascade='all, delete-orphan')
    template = db.relationship('InvoiceTemplate', backref='invoices')
    
    def to_dict(self):
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'company_name': self.company_name,
            'company_address': self.company_address,
            'company_tax_id': self.company_tax_id,
            'company_phone': self.company_phone,
            'company_email': self.company_email,
            'customer_name': self.customer_name,
            'customer_address': self.customer_address,
            'customer_tax_id': self.customer_tax_id,
            'customer_phone': self.customer_phone,
            'customer_email': self.customer_email,
            'subtotal': float(self.subtotal) if self.subtotal else None,
            'tax_amount': float(self.tax_amount) if self.tax_amount else None,
            'total_amount': float(self.total_amount) if self.total_amount else None,
            'currency': self.currency,
            'invoice_date': self.invoice_date.isoformat() if self.invoice_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'created_at': self.created_at.isoformat(),
            'ocr_confidence': self.ocr_confidence,
            'template_id': self.template_id,
            'status': self.status,
            'items': [item.to_dict() for item in self.items]
        }


class InvoiceItem(db.Model):
    __tablename__ = 'invoice_items'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    
    description = db.Column(db.String(500))
    quantity = db.Column(db.Numeric(10, 2))
    unit_price = db.Column(db.Numeric(10, 2))
    total_price = db.Column(db.Numeric(10, 2))
    tax_rate = db.Column(db.Numeric(5, 2))  # Percentage
    
    def to_dict(self):
        return {
            'id': self.id,
            'description': self.description,
            'quantity': float(self.quantity) if self.quantity else None,
            'unit_price': float(self.unit_price) if self.unit_price else None,
            'total_price': float(self.total_price) if self.total_price else None,
            'tax_rate': float(self.tax_rate) if self.tax_rate else None
        }


class InvoiceTemplate(db.Model):
    __tablename__ = 'invoice_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Template structure as JSON
    field_mappings = db.Column(db.Text)  # JSON string of field positions and rules
    ocr_zones = db.Column(db.Text)  # JSON string of OCR extraction zones
    
    # Template metadata
    description = db.Column(db.Text)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Usage statistics
    usage_count = db.Column(db.Integer, default=0)
    success_rate = db.Column(db.Float, default=0.0)
    
    def get_field_mappings(self):
        """Parse field mappings from JSON"""
        if self.field_mappings:
            return json.loads(self.field_mappings)
        return {}
    
    def set_field_mappings(self, mappings):
        """Set field mappings as JSON"""
        self.field_mappings = json.dumps(mappings)
    
    def get_ocr_zones(self):
        """Parse OCR zones from JSON"""
        if self.ocr_zones:
            return json.loads(self.ocr_zones)
        return {}
    
    def set_ocr_zones(self, zones):
        """Set OCR zones as JSON"""
        self.ocr_zones = json.dumps(zones)
    
    def increment_usage(self, success=True):
        """Update usage statistics"""
        self.usage_count += 1
        if success:
            # Update success rate using exponential moving average
            if self.usage_count == 1:
                self.success_rate = 1.0
            else:
                self.success_rate = (self.success_rate * (self.usage_count - 1) + 1.0) / self.usage_count
        else:
            if self.usage_count == 1:
                self.success_rate = 0.0
            else:
                self.success_rate = (self.success_rate * (self.usage_count - 1)) / self.usage_count
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'field_mappings': self.get_field_mappings(),
            'ocr_zones': self.get_ocr_zones(),
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat(),
            'usage_count': self.usage_count,
            'success_rate': self.success_rate
        }


class OCRResult(db.Model):
    __tablename__ = 'ocr_results'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=True)
    template_id = db.Column(db.Integer, db.ForeignKey('invoice_templates.id'), nullable=True)
    
    # OCR processing details
    original_filename = db.Column(db.String(255))
    file_path = db.Column(db.String(500))
    extracted_text = db.Column(db.Text)
    extracted_data = db.Column(db.Text)  # JSON string of extracted structured data
    confidence_score = db.Column(db.Float)
    processing_time = db.Column(db.Float)  # seconds
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Processing status
    status = db.Column(db.String(20), default='processing')  # processing, completed, failed
    error_message = db.Column(db.Text)
    
    # Relationships
    invoice = db.relationship('Invoice', backref='ocr_results')
    template = db.relationship('InvoiceTemplate', backref='ocr_results')
    
    def get_extracted_data(self):
        """Parse extracted data from JSON"""
        if self.extracted_data:
            return json.loads(self.extracted_data)
        return {}
    
    def set_extracted_data(self, data):
        """Set extracted data as JSON"""
        self.extracted_data = json.dumps(data)
    
    def to_dict(self):
        return {
            'id': self.id,
            'invoice_id': self.invoice_id,
            'template_id': self.template_id,
            'original_filename': self.original_filename,
            'extracted_data': self.get_extracted_data(),
            'confidence_score': self.confidence_score,
            'processing_time': self.processing_time,
            'created_at': self.created_at.isoformat(),
            'status': self.status,
            'error_message': self.error_message
        }