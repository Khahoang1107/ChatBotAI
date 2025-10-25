"""
Groq AI Tools for Database Operations
Groq sử dụng các hàm này để thao tác với database
"""

import json
from typing import Dict, Any, List, Optional
from decimal import Decimal
from datetime import datetime, date

class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal and datetime objects"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)

class GroqDatabaseTools:
    """Tools for Groq to interact with database via API"""
    
    def __init__(self, db_tools):
        """Initialize with database tools"""
        self.db_tools = db_tools
    
    def get_all_invoices(self, limit: int = 20, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Lấy danh sách tất cả hóa đơn
        
        Args:
            limit: Số hóa đơn tối đa
            user_id: Lọc theo user (optional)
        
        Returns:
            List of invoices
        """
        try:
            invoices = self.db_tools.get_all_invoices(limit=limit)
            return {
                "success": True,
                "count": len(invoices),
                "invoices": invoices
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_invoices(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Tìm kiếm hóa đơn theo keyword
        
        Args:
            query: Keyword tìm kiếm (code, buyer, amount, etc)
            limit: Số kết quả tối đa
        
        Returns:
            Search results
        """
        try:
            results = self.db_tools.search_invoices(query, limit=limit)
            return {
                "success": True,
                "query": query,
                "count": len(results),
                "results": results
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_invoice_by_id(self, invoice_id: int) -> Dict[str, Any]:
        """
        Lấy chi tiết một hóa đơn
        
        Args:
            invoice_id: Invoice ID
        
        Returns:
            Invoice details
        """
        try:
            invoice = self.db_tools.get_invoice_by_id(invoice_id)
            if invoice:
                return {
                    "success": True,
                    "invoice": invoice
                }
            else:
                return {
                    "success": False,
                    "error": f"Invoice {invoice_id} not found"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Lấy thống kê hóa đơn
        
        Returns:
            Statistics summary
        """
        try:
            stats = self.db_tools.get_statistics()
            return {
                "success": True,
                "statistics": stats
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def filter_by_date(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Lọc hóa đơn theo khoảng thời gian
        
        Args:
            start_date: Ngày bắt đầu (YYYY-MM-DD)
            end_date: Ngày kết thúc (YYYY-MM-DD)
        
        Returns:
            Filtered invoices
        """
        try:
            invoices = self.db_tools.get_all_invoices(limit=1000)
            filtered = []
            for inv in invoices:
                created_at = str(inv.get('created_at', '')).split('T')[0]
                if start_date <= created_at <= end_date:
                    filtered.append(inv)
            
            return {
                "success": True,
                "start_date": start_date,
                "end_date": end_date,
                "count": len(filtered),
                "invoices": filtered
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_invoices_by_type(self, invoice_type: str) -> Dict[str, Any]:
        """
        Lấy hóa đơn theo loại (electricity, water, sale, service)
        
        Args:
            invoice_type: Loại hóa đơn
        
        Returns:
            Invoices of that type
        """
        try:
            invoices = self.db_tools.get_all_invoices(limit=1000)
            filtered = [inv for inv in invoices if inv.get('invoice_type') == invoice_type]
            
            return {
                "success": True,
                "type": invoice_type,
                "count": len(filtered),
                "invoices": filtered
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def save_invoice_from_ocr(self, ocr_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Lưu hóa đơn từ dữ liệu OCR đã extract
        
        Args:
            ocr_data: Dữ liệu OCR đã extract từ extract_invoice_fields()
        
        Returns:
            Save result
        """
        try:
            # Validate required fields
            if not ocr_data.get('invoice_code'):
                return {
                    "success": False,
                    "error": "Missing invoice_code"
                }
            
            # Prepare invoice data for database
            invoice_data = {
                "filename": ocr_data.get('filename', 'ocr_upload.jpg'),
                "invoice_code": ocr_data.get('invoice_code'),
                "invoice_type": ocr_data.get('invoice_type', 'general'),
                "buyer_name": ocr_data.get('buyer_name', 'Unknown'),
                "seller_name": ocr_data.get('seller_name', 'Unknown'),
                "total_amount": ocr_data.get('total_amount', '0 VND'),
                "confidence_score": ocr_data.get('confidence_score', 0.5),
                "raw_text": ocr_data.get('raw_text', ''),
                "invoice_date": ocr_data.get('date', datetime.now().strftime("%d/%m/%Y")),
                "buyer_tax_id": ocr_data.get('buyer_tax_id', ''),
                "seller_tax_id": ocr_data.get('seller_tax_id', ''),
                "buyer_address": ocr_data.get('buyer_address', ''),
                "seller_address": ocr_data.get('seller_address', ''),
                "items": ocr_data.get('items', '[]'),
                "currency": ocr_data.get('currency', 'VND'),
                "subtotal": ocr_data.get('subtotal', 0),
                "tax_amount": ocr_data.get('tax_amount', 0),
                "tax_percentage": ocr_data.get('tax_percentage', 0),
                "total_amount_value": ocr_data.get('total_amount_value', 0),
                "transaction_id": ocr_data.get('transaction_id', ''),
                "payment_method": ocr_data.get('payment_method', ''),
                "payment_account": ocr_data.get('payment_account', ''),
                "invoice_time": ocr_data.get('invoice_time', None),
                "due_date": ocr_data.get('due_date', None)
            }
            
            # Save to database using db_tools
            conn = self.db_tools.connect()
            if not conn:
                return {
                    "success": False,
                    "error": "Cannot connect to database"
                }
            
            with conn.cursor() as cursor:
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
                    invoice_data['filename'],
                    invoice_data['invoice_code'],
                    invoice_data['invoice_type'],
                    invoice_data['buyer_name'],
                    invoice_data['seller_name'],
                    invoice_data['total_amount'],
                    invoice_data['confidence_score'],
                    invoice_data['raw_text'],
                    invoice_data['invoice_date'],
                    invoice_data['buyer_tax_id'],
                    invoice_data['seller_tax_id'],
                    invoice_data['buyer_address'],
                    invoice_data['seller_address'],
                    invoice_data['items'],
                    invoice_data['currency'],
                    invoice_data['subtotal'],
                    invoice_data['tax_amount'],
                    invoice_data['tax_percentage'],
                    invoice_data['total_amount_value'],
                    invoice_data['transaction_id'],
                    invoice_data['payment_method'],
                    invoice_data['payment_account'],
                    invoice_data['invoice_time'],
                    invoice_data['due_date'],
                    datetime.now()
                ))
                result = cursor.fetchone()
                if result:
                    invoice_id = result[0]
                    conn.commit()
                    return {
                        "success": True,
                        "message": f"Invoice saved successfully with ID: {invoice_id}",
                        "invoice_id": invoice_id,
                        "invoice_code": invoice_data['invoice_code']
                    }
                else:
                    conn.commit()
                    return {
                        "success": False,
                        "error": "Invoice inserted but RETURNING failed"
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to save invoice: {str(e)}"
            }
    
    def get_tools_description(self) -> List[Dict[str, Any]]:
        """
        Trả về danh sách các tools mà Groq có thể gọi
        Format cho Groq function calling
        
        Returns:
            List of tools descriptions
        """
        return [
            {
                "name": "get_all_invoices",
                "description": "Lấy danh sách tất cả hóa đơn từ database",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "description": "Số hóa đơn tối đa (default: 20)"},
                        "user_id": {"type": "string", "description": "Lọc theo user (optional)"}
                    }
                }
            },
            {
                "name": "search_invoices",
                "description": "Tìm kiếm hóa đơn theo keyword (code, buyer, amount)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Keyword tìm kiếm"},
                        "limit": {"type": "integer", "description": "Số kết quả tối đa"}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_invoice_by_id",
                "description": "Lấy chi tiết một hóa đơn cụ thể",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "invoice_id": {"type": "integer", "description": "ID của hóa đơn"}
                    },
                    "required": ["invoice_id"]
                }
            },
            {
                "name": "get_statistics",
                "description": "Lấy thống kê tổng quát về hóa đơn",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "filter_by_date",
                "description": "Lọc hóa đơn theo khoảng thời gian",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "start_date": {"type": "string", "description": "Ngày bắt đầu (YYYY-MM-DD)"},
                        "end_date": {"type": "string", "description": "Ngày kết thúc (YYYY-MM-DD)"}
                    },
                    "required": ["start_date", "end_date"]
                }
            },
            {
                "name": "get_invoices_by_type",
                "description": "Lấy hóa đơn theo loại (electricity, water, sale, service)",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "invoice_type": {"type": "string", "description": "Loại hóa đơn"}
                    },
                    "required": ["invoice_type"]
                }
            },
            {
                "name": "save_invoice_from_ocr",
                "description": "Lưu hóa đơn từ dữ liệu OCR đã extract vào database",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ocr_data": {
                            "type": "object",
                            "description": "Dữ liệu OCR đã extract từ extract_invoice_fields()",
                            "properties": {
                                "filename": {"type": "string", "description": "Tên file ảnh"},
                                "invoice_code": {"type": "string", "description": "Mã hóa đơn"},
                                "invoice_type": {"type": "string", "description": "Loại hóa đơn"},
                                "buyer_name": {"type": "string", "description": "Tên người mua"},
                                "seller_name": {"type": "string", "description": "Tên người bán"},
                                "total_amount": {"type": "string", "description": "Tổng tiền"},
                                "date": {"type": "string", "description": "Ngày hóa đơn"},
                                "confidence_score": {"type": "number", "description": "Độ tin cậy"},
                                "raw_text": {"type": "string", "description": "Văn bản OCR gốc"}
                            },
                            "required": ["invoice_code"]
                        }
                    },
                    "required": ["ocr_data"]
                }
            }
        ]
    
    def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Gọi một tool theo tên
        
        Args:
            tool_name: Tên của tool
            **kwargs: Tham số của tool
        
        Returns:
            Kết quả từ tool
        """
        if tool_name == "get_all_invoices":
            return self.get_all_invoices(**kwargs)
        elif tool_name == "search_invoices":
            return self.search_invoices(**kwargs)
        elif tool_name == "get_invoice_by_id":
            return self.get_invoice_by_id(**kwargs)
        elif tool_name == "get_statistics":
            return self.get_statistics()
        elif tool_name == "filter_by_date":
            return self.filter_by_date(**kwargs)
        elif tool_name == "get_invoices_by_type":
            return self.get_invoices_by_type(**kwargs)
        elif tool_name == "get_high_value_invoices":
            return self.get_high_value_invoices(**kwargs)
        elif tool_name == "save_invoice_from_ocr":
            # For save_invoice_from_ocr, ocr_data should be provided by the caller
            # If not provided, this is an error
            if "ocr_data" not in kwargs:
                return {
                    "success": False,
                    "error": "ocr_data parameter is required for save_invoice_from_ocr tool"
                }
            return self.save_invoice_from_ocr(**kwargs)
        else:
            return {
                "success": False,
                "error": f"Tool {tool_name} not found"
            }
    


