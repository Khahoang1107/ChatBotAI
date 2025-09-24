from datetime import datetime
from . import db

class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('templates.id'), nullable=True)
    
    # Basic invoice info
    invoice_number = db.Column(db.String(100), nullable=False)
    invoice_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    
    # Client info
    client_name = db.Column(db.String(200), nullable=False)
    client_email = db.Column(db.String(120), nullable=True)
    client_address = db.Column(db.Text, nullable=True)
    
    # Financial info
    subtotal = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    tax_rate = db.Column(db.Numeric(5, 2), nullable=False, default=0)
    tax_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    
    # Status
    status = db.Column(db.String(20), nullable=False, default='draft')  # draft, sent, paid, overdue
    
    # OCR and file info
    original_file_path = db.Column(db.String(500), nullable=True)
    processed_file_path = db.Column(db.String(500), nullable=True)
    ocr_confidence = db.Column(db.Float, nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True, cascade='all, delete-orphan')
    ocr_results = db.relationship('OCRResult', backref='invoice', lazy=True)
    
    def calculate_totals(self):
        """Calculate subtotal, tax, and total from items"""
        self.subtotal = sum(item.total for item in self.items)
        self.tax_amount = self.subtotal * (self.tax_rate / 100)
        self.total_amount = self.subtotal + self.tax_amount
    
    def to_dict(self):
        """Convert invoice to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'template_id': self.template_id,
            'invoice_number': self.invoice_number,
            'invoice_date': self.invoice_date.isoformat() if self.invoice_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'client_name': self.client_name,
            'client_email': self.client_email,
            'client_address': self.client_address,
            'subtotal': float(self.subtotal),
            'tax_rate': float(self.tax_rate),
            'tax_amount': float(self.tax_amount),
            'total_amount': float(self.total_amount),
            'status': self.status,
            'original_file_path': self.original_file_path,
            'processed_file_path': self.processed_file_path,
            'ocr_confidence': self.ocr_confidence,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'items': [item.to_dict() for item in self.items]
        }
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'


class InvoiceItem(db.Model):
    __tablename__ = 'invoice_items'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    
    description = db.Column(db.String(500), nullable=False)
    quantity = db.Column(db.Numeric(10, 2), nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    total = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def calculate_total(self):
        """Calculate total for this item"""
        self.total = self.quantity * self.unit_price
    
    def to_dict(self):
        """Convert item to dictionary"""
        return {
            'id': self.id,
            'invoice_id': self.invoice_id,
            'description': self.description,
            'quantity': float(self.quantity),
            'unit_price': float(self.unit_price),
            'total': float(self.total),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<InvoiceItem {self.description}>'