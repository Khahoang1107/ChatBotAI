from datetime import datetime
from . import db

class OCRResult(db.Model):
    __tablename__ = 'ocr_results'
    
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # File info
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    
    # OCR results
    extracted_text = db.Column(db.Text, nullable=True)
    confidence_score = db.Column(db.Float, nullable=True)
    processing_time = db.Column(db.Float, nullable=True)  # in seconds
    
    # Parsed data (JSON format)
    parsed_data = db.Column(db.JSON, nullable=True)
    
    # Status
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, processing, completed, failed
    error_message = db.Column(db.Text, nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        """Convert OCR result to dictionary"""
        return {
            'id': self.id,
            'invoice_id': self.invoice_id,
            'user_id': self.user_id,
            'original_filename': self.original_filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'extracted_text': self.extracted_text,
            'confidence_score': self.confidence_score,
            'processing_time': self.processing_time,
            'parsed_data': self.parsed_data,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def __repr__(self):
        return f'<OCRResult {self.original_filename}>'