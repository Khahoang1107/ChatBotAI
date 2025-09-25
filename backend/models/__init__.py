from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

# Import all models
from .user import User
from .invoice import Invoice, InvoiceItem
from .template import InvoiceTemplate, Template
from .ocr_result import OCRResult

__all__ = ['db', 'bcrypt', 'User', 'Invoice', 'InvoiceItem', 'InvoiceTemplate', 'Template', 'OCRResult']