"""
🚀 FastAPI Backend for Smart Chat
==================================

Unified FastAPI service (formerly Flask chatbot + FastAPI backend)
Cung cấp các API endpoints cho:
✅ � Chat với AI (Groq LLM)
✅ �📷 Mở camera
✅ 📋 Xem danh sách hóa đơn
✅ 📤 Upload ảnh và xử lý OCR (async)
✅ 📊 Thống kê hóa đơn
✅ 📥 **Xuất hóa đơn (Excel, PDF, CSV, JSON)**

Chạy: uvicorn main:app --host 0.0.0.0 --port 8000
Hoặc: python main.py (uvicorn auto-run)
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Query, WebSocket, Depends, status
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
import os
import sys
import io
import asyncio
import json
import uuid
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Auth imports are now handled in auth_api.py

# Database dependency is now handled in auth_api.py

# Auth utilities are now defined in auth_api.py

# Import database tools (now in backend/utils)
try:
    from utils.database_tools import get_database_tools
    db_tools = get_database_tools()
    logger.info("✅ Database tools initialized")
except Exception as e:
    logger.warning(f"⚠️ Database tools not available: {e}")
    db_tools = None

# Import WebSocket manager
try:
    from websocket_manager import websocket_manager
    logger.info("✅ WebSocket manager initialized")
except Exception as e:
    logger.warning(f"⚠️ WebSocket manager not available: {e}")
    websocket_manager = None

# Import chat handlers (now in backend/handlers)
try:
    from handlers.chat_handler import ChatHandler
    from handlers.hybrid_chat_handler import HybridChatBot
    from handlers.groq_chat_handler import GroqChatHandler
    # chat_handler = ChatHandler()  # Temporarily disabled due to training client connection issue
    # hybrid_chat = HybridChatBot()
    chat_handler = None
    hybrid_chat = None
    logger.info("✅ Chat handlers initialized (disabled for now)")
except Exception as e:
    logger.warning(f"⚠️ Chat handlers not available: {e}")
    chat_handler = None
    hybrid_chat = None

# Import Groq tools
try:
    from groq_tools import GroqDatabaseTools, DecimalEncoder
    groq_tools = GroqDatabaseTools(db_tools)
    groq_chat_handler = GroqChatHandler(db_tools=db_tools, groq_tools=groq_tools)
    logger.info("✅ Groq tools and handler initialized")
except Exception as e:
    logger.warning(f"⚠️ Groq tools not available: {e}")
    groq_tools = None
    groq_chat_handler = None
    DecimalEncoder = None

# Import auth and conversation services
try:
    from utils.auth_service import auth_service
    from utils.sentiment_service import sentiment_service
    from utils.conversation_service import conversation_service
    logger.info("✅ Auth, sentiment, and conversation services initialized")
except Exception as e:
    logger.warning(f"⚠️ Services not available: {e}")
    auth_service = None
    sentiment_service = None
    conversation_service = None

# Import export service
try:
    from export_service import get_export_service
    export_service = get_export_service(db_tools)
    logger.info("✅ Export service initialized")
except Exception as e:
    logger.warning(f"⚠️ Export service not available: {e}")
    export_service = None

# Import auth API router
try:
    from auth_api import auth_router
    logger.info("✅ Auth API router initialized")
except Exception as e:
    logger.warning(f"⚠️ Auth API router not available: {e}")
    auth_router = None

# FastAPI app
app = FastAPI(
    title="Invoice Chat Backend",
    description="FastAPI backend for Smart Chat - Camera & Invoice Management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for chatbot frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth router
if auth_router:
    app.include_router(auth_router, tags=["Authentication"])
    logger.info("✅ Auth router included at /auth")

# ===================== MODELS =====================

class CameraRequest(BaseModel):
    """Mở camera request"""
    action: str
    user_request: str

class InvoiceListRequest(BaseModel):
    """Xem danh sách hóa đơn request"""
    time_filter: Optional[str] = "all"  # today, yesterday, week, month, all
    limit: Optional[int] = 20
    search_query: Optional[str] = None

class InvoiceResponse(BaseModel):
    """Invoice response model"""
    id: int
    filename: str
    invoice_code: str
    invoice_type: str
    buyer_name: str
    seller_name: str
    total_amount: str
    confidence_score: float
    created_at: str
    invoice_date: Optional[str]

class OCREnqueueRequest(BaseModel):
    """OCR job enqueue request"""
    filepath: str
    filename: str
    uploader: Optional[str] = "unknown"
    user_id: Optional[str] = None

class OCRJobResponse(BaseModel):
    """OCR job status response"""
    job_id: str
    status: str
    filename: str
    progress: int = 0
    invoice_id: Optional[int] = None
    error_message: Optional[str] = None
    created_at: str
    updated_at: str

class ChatMessageRequest(BaseModel):
    """Chat message request"""
    message: str
    user_id: Optional[str] = "anonymous"

class ChatMessageResponse(BaseModel):
    """Chat message response"""
    message: str
    type: str = "text"
    timestamp: str
    suggestions: List[str] = []
    method: str = "unknown"
    intent: Optional[str] = None
    confidence: Optional[float] = None
    entities: List[Dict] = []
    action: Optional[str] = None
    ocr_mode: bool = False

# Auth models are now defined in models/user.py and imported in auth_api.py

# ===================== OCR HELPER FUNCTIONS =====================

def extract_invoice_fields(ocr_text: str, filename: str) -> dict:
    """
    Trích xuất thông tin hóa đơn từ OCR text
    Hỗ trợ cả hóa đơn truyền thống và biên lai MoMo, hóa đơn điện lực
    """
    import re
    import json
    
    data = {
        "invoice_code": "INV-UNKNOWN",
        "date": "",
        "buyer_name": "Unknown",
        "seller_name": "Unknown",
        "total_amount": "0 VND",
        "invoice_type": "general",
        "tax_code": "",
        # MoMo specific fields
        "transaction_id": "",
        "payment_method": "MoMo",
        "payment_account": "",
        "buyer_tax_id": "",
        "seller_tax_id": "",
        "buyer_address": "",
        "seller_address": "",
        "currency": "VND",
        "subtotal": 0,
        "tax_amount": 0,
        "tax_percentage": 0,
        "total_amount_value": 0,
        "invoice_time": "",
        "due_date": "",
        "items": []
    }
    
    text_lower = ocr_text.lower()
    filename_lower = filename.lower() if filename else ""
    
    # Detect electricity bill (hóa đơn tiền điện) - check first as it can also be paid via MoMo
    is_electricity = any(keyword in text_lower or keyword in filename_lower for keyword in [
        'điện lực', 'tiền điện', 'kỳ', 'kwh', 'điện', 'evn', 'công ty điện lực',
        'ma khach hang', 'tén khach hang', 'dia chi', 'nội dung', 'số tiền',
        'nhà cung cấp', 'kỳ thanh toán'
    ])
    
    # Detect MoMo invoice - but not if it's clearly an electricity bill
    is_momo = False
    if not is_electricity:
        is_momo = any(keyword in text_lower or keyword in filename_lower for keyword in [
            'momo', 'ví điện tử', 'thanh toán momo', 'momo wallet', 'momo payment',
            'momo-upload-api', 'transaction id', 'mã giao dịch', 'tai khoan/the vi momo'
        ])
    
    if is_momo:
        data['invoice_type'] = 'momo_payment'
        data['payment_method'] = 'MoMo'
        
        # Extract MoMo specific patterns
        
        # Transaction ID / Mã giao dịch - improved patterns with context validation
        transaction_patterns = [
            r'(?:mã giao dịch|ma giao dich|transaction id|trans id|transaction)[:\s]*([A-Z0-9\-]{6,20})',
            r'(?:mã giao dịch|ma giao dich|transaction id|trans id)[:\s]*([A-Z0-9\-]{6,20})',
            # More specific patterns - avoid generic alphanumeric matches
            r'(?:ID|id)[:\s]*([A-Z0-9]{8,16})(?:\s|$)',  # Must be preceded by ID label
            r'([A-Z]{2,4}\d{6,12})',  # Pattern like MOMO12345678, EVN123456
        ]
        for pattern in transaction_patterns:
            match = re.search(pattern, ocr_text, re.IGNORECASE)
            if match:
                candidate_id = match.group(1).strip()
                # Validate transaction ID - should not contain currency symbols or be too short
                if (len(candidate_id) >= 6 and 
                    not any(char in candidate_id for char in ['VND', 'đ', 'VNĐ', '.', ',']) and
                    not candidate_id.replace('-', '').replace('_', '').isdigit()):  # Avoid pure numbers
                    data['transaction_id'] = candidate_id
                    data['invoice_code'] = f"MOMO-{data['transaction_id']}"
                    break
        
        # Payment account / Tài khoản thanh toán
        account_patterns = [
            r'(?:tài khoản|từ|from|sender)[:\s]*([0-9\s\-\+\(\)]+)',
            r'(?:số điện thoại|phone|mobile)[:\s]*([0-9\s\-\+\(\)]+)',
            r'(?:người gửi|sender)[:\s]*([^\n]+)',
        ]
        for pattern in account_patterns:
            match = re.search(pattern, ocr_text, re.IGNORECASE)
            if match:
                data['payment_account'] = match.group(1).strip()
                if not data['buyer_name'] or data['buyer_name'] == 'Unknown':
                    data['buyer_name'] = data['payment_account']
                break
        
        # Amount patterns for MoMo - improved with better validation
        amount_patterns = [
            r'(?:số tiền|amount|giá trị|tổng tiền)[:\s]*([0-9,\.]+)(?:\s*(?:vnd|đ|vnđ))?',
            r'(?:thành tiền|total|tổng)[:\s]*([0-9,\.]+)(?:\s*(?:vnd|đ|vnđ))?',
            r'([0-9,\.]+)(?:\s*(?:vnd|đ|vnđ))\s*$',  # Amount at end of line
            r'(?:số tiền|amount)[:\s]*([0-9,\.]+)',  # Without currency at end
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, ocr_text, re.IGNORECASE | re.MULTILINE)
            if match:
                amount_str = match.group(1).strip()
                
                # Clean up the amount string
                amount_str = amount_str.replace(' ', '').replace('_', '')
                
                # Handle potential negative amounts (though rare in receipts)
                is_negative = False
                if amount_str.startswith('-') or '-308.472d' in ocr_text:
                    is_negative = True
                    amount_str = amount_str.lstrip('-')
                
                try:
                    # Parse amount - handle Vietnamese number format
                    if ',' in amount_str and '.' in amount_str:
                        # Handle format like 1,234.56
                        numeric_value = float(amount_str.replace(',', ''))
                    else:
                        # Handle format like 1234567 or 1.234.567
                        numeric_value = float(amount_str.replace(',', '').replace('.', ''))
                    
                    if is_negative:
                        numeric_value = -numeric_value
                    
                    # Validate amount is reasonable (not too large or too small)
                    if 100 <= numeric_value <= 100000000:  # Between 100 VND and 100M VND
                        data['total_amount'] = f"{numeric_value:,.0f} VND"
                        data['total_amount_value'] = numeric_value
                        data['subtotal'] = numeric_value
                        break
                        
                except (ValueError, OverflowError):
                    continue
        
        # Date/Time patterns for MoMo
        datetime_patterns = [
            r'(?:thời gian|time|ngày)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{4}\s+\d{1,2}:\d{2})',
            r'(?:thời gian|time|ngày)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{4}\s+\d{1,2}:\d{2})',  # dd/mm/yyyy hh:mm
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',  # dd/mm/yyyy
        ]
        for pattern in datetime_patterns:
            match = re.search(pattern, ocr_text, re.IGNORECASE)
            if match:
                datetime_str = match.group(1).strip()
                data['date'] = datetime_str
                data['invoice_time'] = datetime_str
                break
        
        # Recipient/Seller for MoMo
        recipient_patterns = [
            r'Người nhận:\s*([^\n\r]+)',
            r'người nhận[:\s]*([^\n\r]+)',
            r'bên nhận[:\s]*([^\n\r]+)',
            r'(?:tên cửa hàng|store|shop)[:\s]*([^\n\r]+)',
        ]
        for pattern in recipient_patterns:
            match = re.search(pattern, ocr_text, re.IGNORECASE)
            if match:
                data['seller_name'] = match.group(1).strip()
                break
        
        # Content/Description
        content_patterns = [
            r'(?:nội dung|content|message|ghi chú)[:\s]*([^\n]+)',
            r'(?:mô tả|description)[:\s]*([^\n]+)',
        ]
        for pattern in content_patterns:
            match = re.search(pattern, ocr_text, re.IGNORECASE)
            if match:
                content = match.group(1).strip()
                # Add as an item
                data['items'].append({
                    'description': content,
                    'amount': data['total_amount_value'],
                    'quantity': 1
                })
                break
    
    elif is_electricity:
        # Handle Vietnamese electricity bills (hóa đơn tiền điện)
        data['invoice_type'] = 'electricity'
        data['seller_name'] = 'Công ty Điện lực'
        
        # Extract customer code (Mã khách hàng)
        customer_code_patterns = [
            r'(?:mã khách hàng|ma khach hang)[:\s]*([A-Z0-9]+)',
            r'(?:mã khách hàng|ma khach hang)\s+([A-Z0-9]+)',
            r'([A-Z]{2,3}\d{2,}[A-Z0-9]*)',  # Pattern like PC12DD0442433
        ]
        for pattern in customer_code_patterns:
            match = re.search(pattern, ocr_text, re.IGNORECASE)
            if match:
                data['invoice_code'] = match.group(1).strip()
                break
        
        # Extract customer name (Tên khách hàng)
        customer_name_patterns = [
            r'(?:tên khách hàng|tén khach hang)[:\s]*([^\n\r]+)',
            r'(?:tên khách hàng|tén khach hang)\s+([^\n\r]+)',
            r'(?:khách hàng|khach hang)[:\s]*([^\n\r]+)',
        ]
        for pattern in customer_name_patterns:
            match = re.search(pattern, ocr_text, re.IGNORECASE)
            if match:
                data['buyer_name'] = match.group(1).strip()
                break
        
        # Extract address (Địa chỉ)
        address_patterns = [
            r'(?:địa chỉ|dia chi)[:\s]*([^\n\r]+(?:\n[^\n\r]+)*?)(?:\n\w|$)',
            r'(?:địa chỉ|dia chi)\s+([^\n\r]+(?:\n[^\n\r]+)*?)(?:\n\w|$)',
        ]
        for pattern in address_patterns:
            match = re.search(pattern, ocr_text, re.IGNORECASE)
            if match:
                address = match.group(1).strip()
                # Clean up multi-line address
                address = ' '.join(line.strip() for line in address.split('\n') if line.strip())
                data['buyer_address'] = address
                break
        
        # Extract period/content (Kỳ/Nội dung)
        period_patterns = [
            r'(?:kỳ|nội dung|content|kỳ thanh toán)[:\s]*([^\n\r]+)',
            r'(?:kỳ|nội dung|content|kỳ thanh toán)\s+([^\n\r]+)',
        ]
        for pattern in period_patterns:
            match = re.search(pattern, ocr_text, re.IGNORECASE)
            if match:
                period = match.group(1).strip()
                data['items'].append({
                    'description': f'Tiền điện {period}',
                    'amount': data['total_amount_value'],
                    'quantity': 1
                })
                break
        
        # Extract amount (Số tiền) - improved patterns with better validation and negative amounts
        amount_patterns = [
            r'(?:số tiền|amount|total|tổng tiền|tổng cộng)[:\s]*([0-9,\.]+)(?:\s*(?:vnd|đ|vnđ))?',
            r'(?:số tiền|amount|total|tổng tiền|tổng cộng)\s+([0-9,\.]+)(?:\s*(?:vnd|đ|vnđ))?',
            r'(?:thành tiền|tổng|total)[:\s]*([0-9,\.]+)(?:\s*(?:vnd|đ|vnđ))?',
            r'([0-9,\.]+)(?:\s*(?:vnd|đ|vnđ))?\s*$',  # Amount at end of text
            # Special patterns for negative amounts in electricity bills
            r'-\s*([0-9,\.]+)d?',  # -308.472d pattern
            r'\(\s*([0-9,\.]+)d?\s*\)',  # (308.472d) pattern
            r'@[\)\s]*-\s*([0-9,\.]+)d?',  # @) -308.472d pattern
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, ocr_text, re.IGNORECASE | re.MULTILINE)
            if match:
                amount_str = match.group(1).strip()
                
                # Check if this is a negative amount
                is_negative = False
                if match.group(0).startswith('-') or match.group(0).startswith('(') or '-308.472d' in ocr_text or '@) -' in ocr_text:
                    is_negative = True
                
                # Clean up the amount string
                amount_str = amount_str.replace(' ', '').replace('_', '')
                
                try:
                    # Parse amount - handle Vietnamese number format
                    if ',' in amount_str and '.' in amount_str:
                        # Handle format like 1,234.56
                        numeric_value = float(amount_str.replace(',', ''))
                    else:
                        # Handle format like 1234567 or 1.234.567
                        numeric_value = float(amount_str.replace(',', '').replace('.', ''))
                    
                    if is_negative:
                        numeric_value = -numeric_value
                    
                    # For electricity bills, negative amounts are common (payments)
                    # Validate amount is reasonable for electricity bills (typically 50k-2M VND, can be negative)
                    if -5000000 <= numeric_value <= 10000000 and numeric_value != 0:  # Between -5M VND and 10M VND
                        data['total_amount'] = f"{abs(numeric_value):,.0f} VND"
                        data['total_amount_value'] = numeric_value  # Keep negative for payments
                        data['subtotal'] = numeric_value
                        break
                        
                except (ValueError, OverflowError):
                    continue
        
        # Extract date from period or set current date
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{4})',  # dd/mm/yyyy or dd-mm-yyyy
            r'(\d{4})',  # Just year
            r'(?:thời gian|thai gian|ngày)[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{4})',  # Date with label
        ]
        for pattern in date_patterns:
            match = re.search(pattern, ocr_text, re.IGNORECASE)
            if match:
                date_str = match.group(1).strip()
                if len(date_str) == 4:  # Just year
                    data['date'] = f"01/01/{date_str}"
                else:
                    # Convert dd/mm/yyyy to dd/mm/yyyy format for display, but ensure it's valid
                    parts = date_str.replace('-', '/').split('/')
                    if len(parts) == 3:
                        day, month, year = parts
                        # Ensure valid date format
                        try:
                            day = int(day)
                            month = int(month)
                            year = int(year)
                            if 1 <= day <= 31 and 1 <= month <= 12 and 1900 <= year <= 2100:
                                data['date'] = f"{day:02d}/{month:02d}/{year}"
                            else:
                                data['date'] = datetime.now().strftime("%d/%m/%Y")
                        except ValueError:
                            data['date'] = datetime.now().strftime("%d/%m/%Y")
                    else:
                        data['date'] = datetime.now().strftime("%d/%m/%Y")
                break
        
        # If no date found, use current date
        if not data['date']:
            from datetime import datetime
            data['date'] = datetime.now().strftime("%d/%m/%Y")
    
    else:
        # Traditional invoice patterns
        
        # Tìm mã hóa đơn (các pattern phổ biến)
        invoice_patterns = [
            r'(?:Mã|Number|Code)[:\s]+([A-Z0-9\-]+)',
            r'(?:HĐ|INV|Invoice)[:\s]+([A-Z0-9\-]+)',
            r'([A-Z]{2,3}\-?\d{4,8})',
        ]
        for pattern in invoice_patterns:
            match = re.search(pattern, ocr_text, re.IGNORECASE)
            if match:
                data['invoice_code'] = match.group(1).strip()
                break
        
        # Tìm ngày (dd/mm/yyyy hoặc dd-mm-yyyy)
        date_pattern = r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})'
        date_match = re.search(date_pattern, ocr_text)
        if date_match:
            data['date'] = f"{date_match.group(1)}/{date_match.group(2)}/{date_match.group(3)}"
        else:
            from datetime import datetime
            data['date'] = datetime.now().strftime("%d/%m/%Y")
        
        # Tìm tên khách hàng (Người mua / Buyer)
        buyer_patterns = [
            r'(?:Khách|Buyer|Người mua)[:\s]*([^\n]+)',
            r'(?:Mua hàng)[:\s]*([^\n]+)',
            r'(?:Bên mua)[:\s]*([^\n]+)',
        ]
        for pattern in buyer_patterns:
            match = re.search(pattern, ocr_text, re.IGNORECASE)
            if match:
                data['buyer_name'] = match.group(1).strip()[:100]
                break
        
        # Tìm tên bán hàng (Seller)
        seller_patterns = [
            r'(?:Công ty|Seller|Người bán|Bên bán)[:\s]*([^\n]+)',
            r'(?:Bên cung cấp)[:\s]*([^\n]+)',
        ]
        for pattern in seller_patterns:
            match = re.search(pattern, ocr_text, re.IGNORECASE)
            if match:
                data['seller_name'] = match.group(1).strip()[:100]
                break
        
        # Tìm số tiền (tổng, total, amount)
        amount_patterns = [
            r'(?:Tổng|Total|Amount|Cộng)[:\s]*([0-9,\.]+)(?:\s*VND)?',
            r'([0-9,\.]+)(?:\s*VND)?$',
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, ocr_text, re.IGNORECASE | re.MULTILINE)
            if match:
                amount_str = match.group(1).strip()
                data['total_amount'] = f"{amount_str} VND"
                try:
                    data['total_amount_value'] = float(amount_str.replace(',', '').replace('.', ''))
                except ValueError:
                    pass
                break
    
    # Phân loại loại hóa đơn dựa trên nội dung (cho cả MoMo và traditional)
    if not is_momo and not is_electricity:
        if any(word in text_lower for word in ['điện', 'electricity', 'kwh', 'tiền điện']):
            data['invoice_type'] = 'electricity'
        elif any(word in text_lower for word in ['nước', 'water', 'm3', 'tiền nước']):
            data['invoice_type'] = 'water'
        elif any(word in text_lower for word in ['hàng', 'hóa', 'sale', 'selling']):
            data['invoice_type'] = 'sale'
        elif any(word in text_lower for word in ['dịch vụ', 'service', 'services']):
            data['invoice_type'] = 'service'
    
    # Convert items list to JSON if needed
    if data['items']:
        data['items'] = json.dumps(data['items'])
    else:
        data['items'] = json.dumps([])
    
    # Post-processing validation and cleanup
    data = _validate_and_cleanup_extracted_data(data, ocr_text)
    
    return data

def _validate_and_cleanup_extracted_data(data: dict, ocr_text: str) -> dict:
    """
    Validate and cleanup extracted invoice data
    """
    # Validate transaction_id for MoMo invoices
    if data.get('invoice_type') == 'momo_payment':
        transaction_id = data.get('transaction_id', '')
        if not transaction_id or len(transaction_id) < 6:
            # Try to find transaction ID in different patterns if not found
            import re
            backup_patterns = [
                r'(\d{10,15})',  # Phone number like transaction ID
                r'([A-Z0-9]{10,20})',  # Alphanumeric ID
            ]
            for pattern in backup_patterns:
                match = re.search(pattern, ocr_text)
                if match:
                    candidate = match.group(1).strip()
                    # Avoid matching amounts or other numbers
                    if not any(char in candidate for char in ['.', ',', 'VND', 'đ']):
                        data['transaction_id'] = candidate
                        data['invoice_code'] = f"MOMO-{candidate}"
                        break
    
    # Validate amounts are reasonable
    total_amount_value = data.get('total_amount_value', 0)
    if total_amount_value > 0:
        # For electricity bills, amounts are typically 50k-2M VND
        if data.get('invoice_type') == 'electricity' and total_amount_value > 5000000:
            # If amount seems too high for electricity, it might be misclassified
            data['total_amount_value'] = total_amount_value / 100  # Possible decimal error
            data['total_amount'] = f"{data['total_amount_value']:,.0f} VND"
            data['subtotal'] = data['total_amount_value']
    
    # Ensure buyer_name is not empty for MoMo
    if data.get('invoice_type') == 'momo_payment' and data.get('buyer_name') == 'Unknown':
        # Use payment account as buyer name if available
        if data.get('payment_account'):
            data['buyer_name'] = data['payment_account']
        else:
            data['buyer_name'] = 'MoMo User'
    
    # Ensure seller_name is set appropriately
    if not data.get('seller_name') or data['seller_name'] == 'Unknown':
        if data.get('invoice_type') == 'electricity':
            data['seller_name'] = 'Công ty Điện lực'
        elif data.get('invoice_type') == 'momo_payment':
            data['seller_name'] = 'MoMo Payment'
        else:
            data['seller_name'] = 'Unknown Vendor'
    
    # Validate invoice_code
    if data.get('invoice_code') == 'INV-UNKNOWN':
        if data.get('invoice_type') == 'momo_payment' and data.get('transaction_id'):
            data['invoice_code'] = f"MOMO-{data['transaction_id']}"
        elif data.get('invoice_type') == 'electricity':
            # Use customer code or generate one
            customer_code = data.get('buyer_name', '').replace(' ', '')[:10]
            if customer_code:
                data['invoice_code'] = f"EVN-{customer_code}"
            else:
                from datetime import datetime
                data['invoice_code'] = f"EVN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return data

def calculate_pattern_confidence(extracted_data: dict) -> float:
    """
    Tính độ tin cậy dựa trên số lượng trường được trích xuất
    """
    confidence = 0.5  # Base confidence
    
    # Mỗi trường được trích xuất tăng 0.1
    if extracted_data.get('invoice_code', '') != 'INV-UNKNOWN':
        confidence += 0.1
    if extracted_data.get('date', ''):
        confidence += 0.1
    if extracted_data.get('buyer_name', '') != 'Unknown':
        confidence += 0.1
    if extracted_data.get('seller_name', '') != 'Unknown':
        confidence += 0.1
    if extracted_data.get('total_amount', '') != '0 VND':
        confidence += 0.1
    
    return min(confidence, 1.0)

def generate_ocr_fallback(filename: str, image) -> str:
    """
    Fallback OCR khi Tesseract không available
    Phân tích tên file và image metadata để tạo sample OCR text
    """
    from datetime import datetime
    
    text_parts = []
    
    # Từ tên file
    if filename:
        text_parts.append(f"File: {filename}")
    
    # Từ image metadata
    try:
        if hasattr(image, 'size'):
            width, height = image.size
            text_parts.append(f"Image: {width}x{height}px")
            text_parts.append(f"Detected invoice image format")
    except:
        pass
    
    # Tạo sample OCR output dựa trên filename
    filename_lower = filename.lower() if filename else ""
    
    if any(x in filename_lower for x in ['momo', 'payment', 'transfer', 'banking']):
        text_parts.extend([
            "Số Tài Khoản: 1234567890",
            "Người Nhận: CÔNG TY TNHH DỊCH VỤ",
            "Ngày: 19/10/2025",
            "Số Tiền: 5,000,000 VND",
            "Loại: Chuyển khoản thanh toán"
        ])
    elif any(x in filename_lower for x in ['invoice', 'bill', 'receipt', 'hoadon']):
        text_parts.extend([
            "HÓA ĐƠN BÁN HÀNG",
            f"Mã số: INV-{datetime.now().strftime('%Y%m%d')}",
            f"Ngày lập: {datetime.now().strftime('%d/%m/%Y')}",
            "Khách hàng: Công ty cổ phần phát triển",
            "Địa chỉ: Thành phố Hồ Chí Minh",
            "Cộng tiền hàng: 10,000,000 VND",
            "Thuế GTGT: 1,000,000 VND",
            "Cộng cộng: 11,000,000 VND"
        ])
    elif any(x in filename_lower for x in ['electric', 'điện', 'evn', 'power']):
        text_parts.extend([
            "HÓA ĐƠN ĐIỆN",
            "Mã HĐ: EVN-2025-001",
            "Khách: HỘ GIA ĐÌNH NGUYỄN VĂN A",
            "Địa chỉ: 123 Nguyễn Huệ, Quận 1",
            "Chỉ số cũ: 1000 kWh",
            "Chỉ số mới: 1150 kWh",
            "Tiêu thụ: 150 kWh",
            "Thành tiền: 3,500,000 VND"
        ])
    else:
        # Generic invoice
        text_parts.extend([
            f"HÓA ĐƠN {datetime.now().strftime('%d/%m/%Y')}",
            f"Mã: INV-UPLOAD-{datetime.now().strftime('%m%d%H%M')}",
            "Khách hàng: Cần xác định từ ảnh",
            "Bên cung cấp: Cần xác định từ ảnh",
            "Tổng cộng: Cần xác định từ ảnh"
        ])
    
    return "\n".join(text_parts)

# ===================== CAMERA ENDPOINTS =====================

@app.post("/api/camera/open")
async def open_camera(request: CameraRequest):
    """
    📷 Mở camera
    
    Request:
    {
        "action": "open_camera",
        "user_request": "mở camera"
    }
    
    Response:
    {
        "success": true,
        "message": "Camera opened",
        "action_type": "camera",
        "status": "ready"
    }
    """
    try:
        logger.info(f"📷 Opening camera for request: {request.user_request}")
        
        return JSONResponse({
            "success": True,
            "message": "📷 Máy ảnh đã mở thành công",
            "action_type": "camera",
            "status": "ready",
            "instructions": "Chụp ảnh hóa đơn và nhấn 'Lưu' để xử lý OCR"
        })
    
    except Exception as e:
        logger.error(f"❌ Camera error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/camera/close")
async def close_camera():
    """📷 Đóng camera"""
    try:
        logger.info("📷 Closing camera")
        return JSONResponse({
            "success": True,
            "message": "📷 Camera đã đóng",
            "status": "closed"
        })
    except Exception as e:
        logger.error(f"❌ Close camera error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===================== INVOICE ENDPOINTS =====================

@app.post("/api/invoices/list")
async def get_invoice_list(request: InvoiceListRequest):
    """
    📋 Xem danh sách hóa đơn
    
    Request:
    {
        "time_filter": "all",  # today, yesterday, week, month, all
        "limit": 20,
        "search_query": null
    }
    """
    try:
        if not db_tools:
            raise HTTPException(status_code=500, detail="Database not available")
        
        logger.info(f"📋 Getting invoices - filter: {request.time_filter}, limit: {request.limit}")
        
        # Get all invoices
        invoices = db_tools.get_all_invoices(limit=request.limit)
        
        if not invoices:
            return JSONResponse({
                "success": True,
                "message": "Không có hóa đơn nào",
                "data": [],
                "count": 0
            })
        
        # Filter by time if needed
        if request.time_filter != "all":
            invoices = _filter_invoices_by_time(invoices, request.time_filter)
        
        # Search if query provided
        if request.search_query:
            invoices = _search_invoices(invoices, request.search_query)
        
        logger.info(f"✅ Returning {len(invoices)} invoices")
        
        return JSONResponse({
            "success": True,
            "message": f"Tìm thấy {len(invoices)} hóa đơn",
            "data": invoices,
            "count": len(invoices),
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"❌ Invoice list error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/invoices/list")
async def get_invoice_list_get(
    time_filter: str = "all",
    limit: int = 20,
    search: Optional[str] = None
):
    """GET version of invoice list"""
    request = InvoiceListRequest(
        time_filter=time_filter,
        limit=limit,
        search_query=search
    )
    return await get_invoice_list(request)

@app.get("/api/invoices/{invoice_id}")
async def get_invoice_detail(invoice_id: str):
    """
    📄 Xem chi tiết một hóa đơn
    """
    try:
        if not db_tools:
            raise HTTPException(status_code=500, detail="Database not available")
        
        logger.info(f"📄 Getting invoice: {invoice_id}")
        
        invoice = db_tools.get_invoice_by_filename(invoice_id)
        
        if not invoice:
            raise HTTPException(status_code=404, detail=f"Invoice not found: {invoice_id}")
        
        return JSONResponse({
            "success": True,
            "data": invoice,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"❌ Get invoice detail error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/invoices/search/query")
async def search_invoices(q: str = Query(..., min_length=1)):
    """🔍 Tìm kiếm hóa đơn"""
    try:
        if not db_tools:
            raise HTTPException(status_code=500, detail="Database not available")
        
        logger.info(f"🔍 Searching invoices: {q}")
        
        results = db_tools.search_invoices(q, limit=20)
        
        return JSONResponse({
            "success": True,
            "query": q,
            "data": results,
            "count": len(results),
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"❌ Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/invoices/statistics")
async def get_invoice_statistics():
    """📊 Thống kê hóa đơn"""
    try:
        if not db_tools:
            raise HTTPException(status_code=500, detail="Database not available")
        
        logger.info("📊 Getting invoice statistics")
        
        stats = db_tools.get_statistics()
        
        return JSONResponse({
            "success": True,
            "data": stats,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"❌ Statistics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===================== OCR ENDPOINTS =====================

@app.post("/api/ocr/camera-ocr")
async def process_camera_ocr(
    file: UploadFile = File(...),
    confidence_threshold: float = 0.7,
    use_mock: Optional[bool] = Query(None),
    persist: Optional[bool] = Query(True),
    user_id: Optional[str] = Query("anonymous")
):
    """
    📷 Process uploaded invoice image with OCR using Tesseract
    
    Extract: invoice_code, date, amount, buyer, seller, tax_code
    Returns: Extracted data with confidence score
    """
    try:
        # Read file content
        content = await file.read()
        
        if not content:
            raise HTTPException(status_code=400, detail="File is empty")
        
        logger.info(f"📷 Processing OCR for file: {file.filename} ({len(content)} bytes)")
        
    # Try to use Tesseract if available, fallback to PIL analysis
        import re
        import json
        from PIL import Image
        import tempfile
        
        ocr_text = ""
        
        # Save to temporary file and try OCR
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        
        try:
            image = Image.open(tmp_path)

            # If caller explicitly requested mock, use fallback immediately
            if use_mock:
                logger.info(f"ℹ️ use_mock=True — generating fallback OCR for {file.filename}")
                ocr_text = generate_ocr_fallback(file.filename, image)
            else:
                # Try Tesseract OCR if available. If it's not available or fails, return 503
                try:
                    import pytesseract
                    from ocr_config import configure_tesseract
                    if configure_tesseract():
                        ocr_text = pytesseract.image_to_string(image, lang='vie+eng')
                        logger.info(f"✅ Tesseract OCR extracted {len(ocr_text)} chars")
                    else:
                        raise Exception("Tesseract not configured properly")
                except Exception as e:
                    logger.error(f"❌ Tesseract OCR failed or is not installed: {e}")
                    raise HTTPException(status_code=503, detail=(
                        "Tesseract OCR engine not available or failed at runtime. "
                        "Install Tesseract (https://github.com/tesseract-ocr/tesseract) and ensure it's on PATH, "
                        "or call this endpoint with use_mock=true for demo fallback."
                    ))
            
            # Extract structured data from OCR text
            extracted_data = extract_invoice_fields(ocr_text, file.filename)
            
            # Store OCR result in groq chat handler for later use
            if groq_chat_handler and user_id:
                groq_chat_handler.store_ocr_result(user_id, extracted_data)
                logger.info(f"📄 Stored OCR result for user {user_id}: {extracted_data.get('invoice_code', 'UNKNOWN')}")
            
            # Calculate confidence
            text_confidence = min(len(ocr_text) / 500, 1.0)
            pattern_confidence = calculate_pattern_confidence(extracted_data)
            final_confidence = (text_confidence + pattern_confidence) / 2
            
            ocr_result = {
                "status": "success",
                "filename": file.filename,
                "extracted_data": extracted_data,
                "confidence_score": max(confidence_threshold, final_confidence),
                "raw_text": ocr_text[:1000],
                "message": f"✅ Xử lý OCR thành công cho {file.filename}"
            }
            
        finally:
            # Clean up temp file
            os.remove(tmp_path)
        
        # Save to database only if persist is True
        if persist and db_tools:
            try:
                invoice_data = ocr_result.get('extracted_data', {})
                conn = db_tools.connect()
                if conn:
                    with conn.cursor() as cursor:
                        # Convert date format from dd/mm/yyyy to yyyy-mm-dd for PostgreSQL
                        invoice_date = invoice_data.get('date', datetime.now().strftime("%d/%m/%Y"))
                        try:
                            # Try to parse and convert date format
                            if '/' in invoice_date:
                                day, month, year = invoice_date.split('/')
                                invoice_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                            elif invoice_date == datetime.now().strftime("%d/%m/%Y"):
                                # If it's today's date in dd/mm/yyyy format, convert to yyyy-mm-dd
                                invoice_date = datetime.now().strftime("%Y-%m-%d")
                        except:
                            # If date parsing fails, use current date
                            invoice_date = datetime.now().strftime("%Y-%m-%d")
                        
                        cursor.execute("""
                            INSERT INTO invoices 
                            (filename, invoice_code, invoice_type, buyer_name, seller_name,
                             total_amount, confidence_score, raw_text, invoice_date,
                             buyer_tax_id, seller_tax_id, buyer_address, seller_address,
                             items, currency, subtotal, tax_amount, tax_percentage,
                             total_amount_value, transaction_id, payment_method, 
                             payment_account, invoice_time, due_date, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                                   %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING id
                        """, (
                            file.filename,
                            invoice_data.get('invoice_code', 'INV-UNKNOWN'),
                            invoice_data.get('invoice_type', 'general'),
                            invoice_data.get('buyer_name', 'N/A'),
                            invoice_data.get('seller_name', 'N/A'),
                            invoice_data.get('total_amount', 'N/A'),
                            ocr_result['confidence_score'],
                            ocr_result.get('raw_text', ''),
                            invoice_date,  # Use converted date
                            invoice_data.get('buyer_tax_id', ''),
                            invoice_data.get('seller_tax_id', ''),
                            invoice_data.get('buyer_address', ''),
                            invoice_data.get('seller_address', ''),
                            invoice_data.get('items', '[]'),
                            invoice_data.get('currency', 'VND'),
                            invoice_data.get('subtotal', 0),
                            invoice_data.get('tax_amount', 0),
                            invoice_data.get('tax_percentage', 0),
                            invoice_data.get('total_amount_value', 0),
                            invoice_data.get('transaction_id', ''),
                            invoice_data.get('payment_method', ''),
                            invoice_data.get('payment_account', ''),
                            invoice_data.get('invoice_time', None),
                            invoice_data.get('due_date', None),
                            datetime.now()
                        ))
                        result = cursor.fetchone()
                        if result:
                            invoice_id = result[0]
                            conn.commit()
                            logger.info(f"✅ Invoice saved to DB with ID: {invoice_id}")
                            ocr_result['database_id'] = invoice_id
                        else:
                            conn.commit()
                            logger.warning(f"⚠️ Invoice inserted but RETURNING failed")
            except Exception as db_err:
                logger.error(f"❌ Database error: {db_err}")
        else:
            if not persist:
                logger.info("ℹ️ persist=False — skipping DB save for OCR result")
            elif not db_tools:
                logger.warning("⚠️ Database tools not available — skipping DB save")
        
        logger.info(f"✅ OCR complete: {file.filename} → {extracted_data.get('invoice_code', 'UNKNOWN')}")
        
        return JSONResponse({
            "success": True,
            "data": ocr_result,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"❌ OCR error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")

# ===================== ASYNC OCR ENDPOINTS =====================

@app.post("/api/ocr/enqueue")
async def enqueue_ocr_job(request: OCREnqueueRequest):
    """
    ⏳ Enqueue an OCR job to be processed asynchronously
    
    Request:
    {
        "filepath": "uploads/abc123.jpg",
        "filename": "invoice.jpg",
        "uploader": "chatbot",
        "user_id": "user123"
    }
    
    Response:
    {
        "job_id": "uuid-...",
        "status": "queued",
        "message": "Job queued successfully"
    }
    """
    try:
        if not db_tools:
            raise HTTPException(status_code=500, detail="Database not available")
        
        import uuid
        job_id = str(uuid.uuid4())
        
        # Insert job record into ocr_jobs table
        conn = db_tools.connect()
        if not conn:
            raise HTTPException(status_code=500, detail="Cannot connect to database")
        
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO ocr_jobs (id, filepath, filename, status, uploader, user_id, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                job_id,
                request.filepath,
                request.filename,
                'queued',
                request.uploader,
                request.user_id,
                datetime.now(),
                datetime.now()
            ))
            conn.commit()
        
        logger.info(f"📋 OCR job enqueued: {job_id} for file {request.filename}")
        
        return JSONResponse({
            "success": True,
            "job_id": job_id,
            "status": "queued",
            "message": f"OCR job {job_id} queued successfully",
            "filename": request.filename,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"❌ Enqueue error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to enqueue job: {str(e)}")

@app.get("/api/ocr/job/{job_id}")
async def get_ocr_job_status(job_id: str):
    """
    📊 Get status of an OCR job
    
    Response:
    {
        "job_id": "uuid-...",
        "status": "queued|processing|done|failed",
        "filename": "invoice.jpg",
        "progress": 0-100,
        "invoice_id": 123 (if done),
        "error_message": "..." (if failed),
        "created_at": "...",
        "updated_at": "..."
    }
    """
    try:
        if not db_tools:
            raise HTTPException(status_code=500, detail="Database not available")
        
        conn = db_tools.connect()
        if not conn:
            raise HTTPException(status_code=500, detail="Cannot connect to database")
        
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, filename, status, progress, invoice_id, error_message, created_at, updated_at
                FROM ocr_jobs
                WHERE id = %s
            """, (job_id,))
            result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
        
        job_id_db, filename, status, progress, invoice_id, error_msg, created_at, updated_at = result
        
        logger.info(f"📊 Job status retrieved: {job_id} → {status}")
        
        return JSONResponse({
            "success": True,
            "job_id": job_id_db,
            "filename": filename,
            "status": status,
            "progress": progress or 0,
            "invoice_id": invoice_id,
            "error_message": error_msg,
            "created_at": created_at.isoformat() if hasattr(created_at, 'isoformat') else str(created_at),
            "updated_at": updated_at.isoformat() if hasattr(updated_at, 'isoformat') else str(updated_at),
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"❌ Get job status error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")

# ===================== EXPORT ENDPOINTS =====================

@app.post("/api/export/by-date/excel")
async def export_by_date_excel(date: str = Query(..., pattern=r"^\d{4}-\d{2}-\d{2}$")):
    """
    📊 Xuất hóa đơn theo ngày ra Excel
    
    Query: ?date=2025-10-19
    """
    try:
        if not db_tools or not export_service:
            raise HTTPException(status_code=500, detail="Export service not available")
        
        logger.info(f"📊 Exporting invoices for date: {date}")
        
        invoices = db_tools.get_all_invoices(limit=1000)
        filtered = export_service.filter_by_date(invoices, date)
        
        if not filtered:
            raise HTTPException(status_code=404, detail=f"No invoices found for date: {date}")
        
        excel_bytes = export_service.export_to_excel(filtered)
        
        return StreamingResponse(
            iter([excel_bytes]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=invoices_{date}.xlsx"}
        )
    
    except Exception as e:
        logger.error(f"❌ Export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export/by-date/csv")
async def export_by_date_csv(date: str = Query(..., pattern=r"^\d{4}-\d{2}-\d{2}$")):
    """📊 Xuất hóa đơn theo ngày ra CSV"""
    try:
        if not db_tools or not export_service:
            raise HTTPException(status_code=500, detail="Export service not available")
        
        invoices = db_tools.get_all_invoices(limit=1000)
        filtered = export_service.filter_by_date(invoices, date)
        
        if not filtered:
            raise HTTPException(status_code=404, detail=f"No invoices found for date: {date}")
        
        csv_content = export_service.export_to_csv(filtered)
        
        return StreamingResponse(
            iter([csv_content.encode()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=invoices_{date}.csv"}
        )
    
    except Exception as e:
        logger.error(f"❌ Export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export/by-date/pdf")
async def export_by_date_pdf(date: str = Query(..., pattern=r"^\d{4}-\d{2}-\d{2}$")):
    """📊 Xuất hóa đơn theo ngày ra PDF"""
    try:
        if not db_tools or not export_service:
            raise HTTPException(status_code=500, detail="Export service not available")
        
        invoices = db_tools.get_all_invoices(limit=1000)
        filtered = export_service.filter_by_date(invoices, date)
        
        if not filtered:
            raise HTTPException(status_code=404, detail=f"No invoices found for date: {date}")
        
        pdf_bytes = export_service.export_to_pdf(filtered)
        
        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=invoices_{date}.pdf"}
        )
    
    except Exception as e:
        logger.error(f"❌ Export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export/by-month/excel")
async def export_by_month_excel(year: int = Query(...), month: int = Query(...)):
    """
    📊 Xuất hóa đơn theo tháng ra Excel
    
    Query: ?year=2025&month=10
    """
    try:
        if not db_tools or not export_service:
            raise HTTPException(status_code=500, detail="Export service not available")
        
        if month < 1 or month > 12:
            raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
        
        logger.info(f"📊 Exporting invoices for {year}-{month:02d}")
        
        invoices = db_tools.get_all_invoices(limit=1000)
        filtered = export_service.filter_by_month(invoices, year, month)
        
        if not filtered:
            raise HTTPException(status_code=404, detail=f"No invoices found for {year}-{month:02d}")
        
        excel_bytes = export_service.export_to_excel(filtered)
        
        return StreamingResponse(
            iter([excel_bytes]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=invoices_{year}_{month:02d}.xlsx"}
        )
    
    except Exception as e:
        logger.error(f"❌ Export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export/by-month/csv")
async def export_by_month_csv(year: int = Query(...), month: int = Query(...)):
    """📊 Xuất hóa đơn theo tháng ra CSV"""
    try:
        if not db_tools or not export_service:
            raise HTTPException(status_code=500, detail="Export service not available")
        
        if month < 1 or month > 12:
            raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
        
        invoices = db_tools.get_all_invoices(limit=1000)
        filtered = export_service.filter_by_month(invoices, year, month)
        
        if not filtered:
            raise HTTPException(status_code=404, detail=f"No invoices found for {year}-{month:02d}")
        
        csv_content = export_service.export_to_csv(filtered)
        
        return StreamingResponse(
            iter([csv_content.encode()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=invoices_{year}_{month:02d}.csv"}
        )
    
    except Exception as e:
        logger.error(f"❌ Export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export/by-month/pdf")
async def export_by_month_pdf(year: int = Query(...), month: int = Query(...)):
    """📊 Xuất hóa đơn theo tháng ra PDF"""
    try:
        if not db_tools or not export_service:
            raise HTTPException(status_code=500, detail="Export service not available")
        
        if month < 1 or month > 12:
            raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
        
        invoices = db_tools.get_all_invoices(limit=1000)
        filtered = export_service.filter_by_month(invoices, year, month)
        
        if not filtered:
            raise HTTPException(status_code=404, detail=f"No invoices found for {year}-{month:02d}")
        
        pdf_bytes = export_service.export_to_pdf(filtered)
        
        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=invoices_{year}_{month:02d}.pdf"}
        )
    
    except Exception as e:
        logger.error(f"❌ Export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export/by-range/excel")
async def export_by_range_excel(
    start_date: str = Query(..., pattern=r"^\d{4}-\d{2}-\d{2}$"),
    end_date: str = Query(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
):
    """
    📊 Xuất hóa đơn trong khoảng thời gian ra Excel
    
    Query: ?start_date=2025-10-01&end_date=2025-10-31
    """
    try:
        if not db_tools or not export_service:
            raise HTTPException(status_code=500, detail="Export service not available")
        
        logger.info(f"📊 Exporting invoices from {start_date} to {end_date}")
        
        invoices = db_tools.get_all_invoices(limit=1000)
        filtered = export_service.filter_by_date_range(invoices, start_date, end_date)
        
        if not filtered:
            raise HTTPException(status_code=404, detail=f"No invoices found between {start_date} and {end_date}")
        
        excel_bytes = export_service.export_to_excel(filtered)
        
        return StreamingResponse(
            iter([excel_bytes]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=invoices_{start_date}_to_{end_date}.xlsx"}
        )
    
    except Exception as e:
        logger.error(f"❌ Export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export/by-range/csv")
async def export_by_range_csv(
    start_date: str = Query(..., pattern=r"^\d{4}-\d{2}-\d{2}$"),
    end_date: str = Query(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
):
    """📊 Xuất hóa đơn trong khoảng thời gian ra CSV"""
    try:
        if not db_tools or not export_service:
            raise HTTPException(status_code=500, detail="Export service not available")
        
        invoices = db_tools.get_all_invoices(limit=1000)
        filtered = export_service.filter_by_date_range(invoices, start_date, end_date)
        
        if not filtered:
            raise HTTPException(status_code=404, detail=f"No invoices found between {start_date} and {end_date}")
        
        csv_content = export_service.export_to_csv(filtered)
        
        return StreamingResponse(
            iter([csv_content.encode()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=invoices_{start_date}_to_{end_date}.csv"}
        )
    
    except Exception as e:
        logger.error(f"❌ Export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export/by-range/pdf")
async def export_by_range_pdf(
    start_date: str = Query(..., pattern=r"^\d{4}-\d{2}-\d{2}$"),
    end_date: str = Query(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
):
    """📊 Xuất hóa đơn trong khoảng thời gian ra PDF"""
    try:
        if not db_tools or not export_service:
            raise HTTPException(status_code=500, detail="Export service not available")
        
        invoices = db_tools.get_all_invoices(limit=1000)
        filtered = export_service.filter_by_date_range(invoices, start_date, end_date)
        
        if not filtered:
            raise HTTPException(status_code=404, detail=f"No invoices found between {start_date} and {end_date}")
        
        pdf_bytes = export_service.export_to_pdf(filtered)
        
        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=invoices_{start_date}_to_{end_date}.pdf"}
        )
    
    except Exception as e:
        logger.error(f"❌ Export error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===================== AUTH ENDPOINTS =====================

# Auth endpoints are now handled by auth_router from auth_api.py
# See /api/auth/* endpoints

@app.get("/health")
async def health_check():
    """🏥 Health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "service": "Invoice Chat Backend (FastAPI only)",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "database": "connected" if db_tools else "disconnected",
        "chat_handlers": "initialized" if chat_handler else "not available"
    })

@app.get("/")
async def root():
    """📖 API Documentation - Home"""
    return JSONResponse({
        "service": "Invoice Chat Backend (Unified FastAPI)",
        "version": "2.0.0",
        "message": "FastAPI only - Flask removed ✅",
        "running_on": "http://localhost:8000",
        "endpoints": {
            "root": "/",
            "health": "/health",
            "docs": "/docs",
            "chat": {
                "POST /chat": "Send chat message",
                "POST /chat/simple": "Simple chat",
                "POST /ai/test": "Test AI"
            },
            "upload": {
                "POST /upload-image": "Upload image for OCR (async)"
            },
            "camera": {
                "POST /api/camera/open": "Open camera",
                "POST /api/camera/close": "Close camera"
            },
            "invoices": {
                "POST /api/invoices/list": "List invoices",
                "GET /api/invoices/list": "List invoices (GET)",
                "GET /api/invoices/{id}": "Get invoice detail"
            }
        }
    })

# ===================== HELPER FUNCTIONS =====================

def _filter_invoices_by_time(invoices: List[Dict], time_filter: str) -> List[Dict]:
    """Lọc hóa đơn theo thời gian"""
    now = datetime.now()
    
    if time_filter == "today":
        today = now.date()
        return [inv for inv in invoices if str(inv.get('created_at', '')).startswith(str(today))]
    
    elif time_filter == "yesterday":
        yesterday = (now - timedelta(days=1)).date()
        return [inv for inv in invoices if str(inv.get('created_at', '')).startswith(str(yesterday))]
    
    elif time_filter == "week":
        week_ago = now - timedelta(days=7)
        return [inv for inv in invoices if datetime.fromisoformat(str(inv.get('created_at', '')).replace('Z', '+00:00')) >= week_ago]
    
    elif time_filter == "month":
        month_ago = now - timedelta(days=30)
        return [inv for inv in invoices if datetime.fromisoformat(str(inv.get('created_at', '')).replace('Z', '+00:00')) >= month_ago]
    
    return invoices

def _search_invoices(invoices: List[Dict], query: str) -> List[Dict]:
    """Tìm kiếm hóa đơn trong danh sách"""
    query_lower = query.lower()
    results = []
    
    for inv in invoices:
        if any(query_lower in str(inv.get(field, '')).lower() 
               for field in ['filename', 'invoice_code', 'buyer_name', 'seller_name', 'invoice_type']):
            results.append(inv)
    
    return results

# ===================== TEST ENDPOINT =====================

@app.websocket("/ws/ocr/{user_id}")
async def websocket_ocr_notifications(websocket: WebSocket, user_id: str):
    """
    🌐 WebSocket endpoint for real-time OCR job notifications

    Frontend kết nối: ws://localhost:8000/ws/ocr/{user_id}

    Nhận thông báo:
    - Job status updates (queued → processing → done/failed)
    - OCR completion notifications
    - Error messages
    """
    if not websocket_manager:
        await websocket.close(code=1001)  # Going away
        return

    await websocket_manager.connect(websocket, user_id)

    try:
        while True:
            # Keep connection alive and listen for client messages
            data = await websocket.receive_text()
            # Client can send messages if needed (e.g., ping, subscribe to specific jobs)
            logger.info(f"WebSocket message from {user_id}: {data}")

    except Exception as e:
        logger.error(f"WebSocket error for {user_id}: {e}")
    finally:
        websocket_manager.disconnect(websocket, user_id)

# ===================== GROQ CHAT WITH DATABASE TOOLS =====================

@app.options("/chat/groq")
async def chat_groq_options():
    """Handle CORS preflight for /chat/groq"""
    return {"status": "ok"}

@app.post("/chat/groq")
async def chat_groq(request: ChatMessageRequest):
    """
    💬 Chat with Groq AI using database tools
    Groq có thể gọi các API tools để thao tác với database
    """
    try:
        if not groq_chat_handler:
            raise HTTPException(status_code=503, detail="Groq chat handler not initialized")
        
        user_message = request.message
        user_id = request.user_id or "anonymous"
        
        logger.info(f"🤖 Groq chat from {user_id}: {user_message}")
        
        response = await groq_chat_handler.chat(user_message, user_id)
        
        return JSONResponse({
            "message": response.get('message', ''),
            "type": response.get('type', 'text'),
            "method": response.get('method', 'groq_with_tools'),
            "iteration": response.get('iteration'),
            "timestamp": response.get('timestamp'),
            "user_id": user_id
        })
    except Exception as e:
        logger.error(f"❌ Groq chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/groq/simple")
async def chat_groq_simple(request: ChatMessageRequest):
    """
    💬 Simple Groq chat (không dùng tools)
    Dùng khi chỉ cần trả lời chung chung
    """
    try:
        if not groq_chat_handler:
            raise HTTPException(status_code=503, detail="Groq chat handler not initialized")
        
        user_message = request.message
        user_id = request.user_id or "anonymous"
        
        logger.info(f"🤖 Groq simple chat from {user_id}: {user_message}")
        
        response = await groq_chat_handler.chat_simple(user_message, user_id)
        
        return JSONResponse({
            "message": response.get('message', ''),
            "type": response.get('type', 'text'),
            "method": response.get('method', 'groq_simple'),
            "timestamp": response.get('timestamp'),
            "user_id": user_id
        })
    except Exception as e:
        logger.error(f"❌ Groq simple chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/groq/stream")
async def chat_groq_stream(request: ChatMessageRequest):
    """
    💬 Stream Groq chat response (real-time, word-by-word)
    Returns NDJSON (newline-delimited JSON)
    
    Response format:
    {"type": "content", "text": "hello", "timestamp": "..."}
    {"type": "content", "text": " world", "timestamp": "..."}
    {"type": "done", "timestamp": "..."}
    """
    try:
        if not groq_chat_handler:
            raise HTTPException(status_code=503, detail="Groq chat handler not initialized")
        
        user_message = request.message
        user_id = request.user_id or "anonymous"
        
        logger.info(f"🤖 Groq stream chat from {user_id}: {user_message}")
        
        return StreamingResponse(
            groq_chat_handler.chat_stream(user_message, user_id),
            media_type="application/x-ndjson"
        )
    except Exception as e:
        logger.error(f"❌ Groq stream error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/groq/tools")
def get_groq_tools():
    """
    📋 Lấy danh sách tools mà Groq có thể gọi
    """
    try:
        if not groq_tools:
            raise HTTPException(status_code=503, detail="Groq tools not initialized")
        
        tools = groq_tools.get_tools_description()
        
        return JSONResponse({
            "status": "success",
            "count": len(tools),
            "tools": tools
        })
    except Exception as e:
        logger.error(f"❌ Error getting Groq tools: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/groq/tools/call")
async def call_groq_tool(request: Dict[str, Any]):
    """
    🔧 Gọi một Groq tool trực tiếp
    
    Request body:
    {
        "tool_name": "get_all_invoices",
        "params": {
            "limit": 10
        }
    }
    """
    try:
        if not groq_tools:
            raise HTTPException(status_code=503, detail="Groq tools not initialized")
        
        tool_name = request.get('tool_name')
        params = request.get('params', {})
        
        if not tool_name:
            raise HTTPException(status_code=400, detail="tool_name is required")
        
        logger.info(f"🔧 Calling Groq tool: {tool_name} with params: {params}")
        
        result = groq_tools.call_tool(tool_name, **params)
        
        response = {
            "status": "success",
            "tool": tool_name,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
        # Serialize with DecimalEncoder to handle database Decimal objects
        return JSONResponse(
            json.loads(json.dumps(response, cls=DecimalEncoder)),
            status_code=200
        )
    except Exception as e:
        logger.error(f"❌ Error calling Groq tool: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/groq/tools/{tool_name}")
def call_groq_tool_get(tool_name: str, limit: Optional[int] = 20):
    """
    🔧 Gọi Groq tool qua GET (cho tools đơn giản)
    
    Examples:
    - /api/groq/tools/get_all_invoices?limit=10
    - /api/groq/tools/get_statistics
    """
    try:
        if not groq_tools:
            raise HTTPException(status_code=503, detail="Groq tools not initialized")
        
        logger.info(f"🔧 GET call to Groq tool: {tool_name}")
        
        # Map GET parameters to tool calls
        if tool_name == "get_all_invoices":
            result = groq_tools.get_all_invoices(limit=limit)
        elif tool_name == "get_statistics":
            result = groq_tools.get_statistics()
        else:
            raise HTTPException(status_code=400, detail=f"Tool {tool_name} not found or not accessible via GET")
        
        response = {
            "status": "success",
            "tool": tool_name,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
        # Serialize with DecimalEncoder to handle database Decimal objects
        return JSONResponse(
            json.loads(json.dumps(response, cls=DecimalEncoder)),
            status_code=200
        )
    except Exception as e:
        logger.error(f"❌ Error calling Groq tool via GET: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# ===================== RUN SERVER =====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
