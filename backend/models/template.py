from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

class TemplateTypeEnum(enum.Enum):
    WORD = "word"
    PDF = "pdf"
    EXCEL = "excel"

class InvoiceTemplate(Base):
    __tablename__ = "invoice_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    content = Column(Text, nullable=False)  # Lưu nội dung HTML/XML của template
    template_type = Column(Enum(TemplateTypeEnum), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<InvoiceTemplate(id={self.id}, name='{self.name}', type='{self.template_type}')>"
    
    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "content": self.content,
            "template_type": self.template_type.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

# Alias để tương thích với import
Template = InvoiceTemplate