# Pydantic Request/Response Models

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v


class UserResponse(UserBase):
    id: int
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int


class MessageBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)


class MessageCreate(MessageBase):
    pass


class MessageResponse(MessageBase):
    id: int
    sender: str
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    tokens_used: int


class FileUploadResponse(BaseModel):
    file_id: str
    filename: str
    file_size: int
    upload_at: datetime


class OCRResult(BaseModel):
    file_id: str
    extracted_text: str
    confidence: float
    processing_time: float


class InvoiceBase(BaseModel):
    invoice_number: str
    amount: float = Field(..., gt=0)
    date: datetime
    vendor: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    pass


class InvoiceResponse(InvoiceBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[dict] = None
    request_id: Optional[str] = None
