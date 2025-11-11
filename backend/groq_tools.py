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
    
    def export_to_excel(self, filter_type: str = "all", start_date: str = None, end_date: str = None, invoice_type: str = None) -> Dict[str, Any]:
        """
        Xuất danh sách hóa đơn ra file Excel
        
        Args:
            filter_type: Loại filter ("all", "today", "date_range", "type")
            start_date: Ngày bắt đầu (YYYY-MM-DD) - cho date_range
            end_date: Ngày kết thúc (YYYY-MM-DD) - cho date_range  
            invoice_type: Loại hóa đơn - cho type filter
        
        Returns:
            Thông tin về file Excel đã tạo
        """
        try:
            # Lấy dữ liệu theo filter
            if filter_type == "all":
                invoices = self.db_tools.get_all_invoices(limit=1000)
                filter_desc = "tất cả"
            elif filter_type == "today":
                from datetime import datetime
                today = datetime.now().strftime("%Y-%m-%d")
                all_invoices = self.db_tools.get_all_invoices(limit=1000)
                invoices = []
                for inv in all_invoices:
                    created_str = str(inv.get('created_at', ''))
                    if created_str.startswith(today):
                        invoices.append(inv)
                filter_desc = f"hôm nay ({today})"
            elif filter_type == "date_range" and start_date and end_date:
                all_invoices = self.db_tools.get_all_invoices(limit=1000)
                invoices = []
                for inv in all_invoices:
                    created_str = str(inv.get('created_at', ''))
                    inv_date = created_str.split('T')[0] if 'T' in created_str else created_str
                    if start_date <= inv_date <= end_date:
                        invoices.append(inv)
                filter_desc = f"từ {start_date} đến {end_date}"
            elif filter_type == "type" and invoice_type:
                all_invoices = self.db_tools.get_all_invoices(limit=1000)
                invoices = [inv for inv in all_invoices if inv.get('invoice_type') == invoice_type]
                filter_desc = f"loại {invoice_type}"
            else:
                return {
                    "success": False,
                    "error": "Invalid filter parameters"
                }
            
            if not invoices:
                return {
                    "success": False,
                    "error": f"Không có hóa đơn nào cho filter: {filter_desc}"
                }
            
            # Tạo file Excel
            from export_service import get_export_service
            export_service = get_export_service(self.db_tools)
            excel_bytes = export_service.export_to_excel(invoices)
            
            if not excel_bytes:
                return {
                    "success": False,
                    "error": "Không thể tạo file Excel"
                }
            
            # Lưu file tạm thời và trả về URL
            import tempfile
            import os
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"invoices_{filter_type}_{timestamp}.xlsx"
            
            # Tạo thư mục temp nếu chưa có
            temp_dir = os.path.join(os.getcwd(), "temp_exports")
            os.makedirs(temp_dir, exist_ok=True)
            
            file_path = os.path.join(temp_dir, filename)
            
            with open(file_path, 'wb') as f:
                f.write(excel_bytes)
            
            # Tạo URL để download (giả định server chạy trên localhost:8000)
            download_url = f"http://localhost:8000/api/export/download/{filename}"
            
            return {
                "success": True,
                "message": f"Đã xuất {len(invoices)} hóa đơn {filter_desc} ra file Excel",
                "filename": filename,
                "download_url": download_url,
                "file_size": len(excel_bytes),
                "invoice_count": len(invoices)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Lỗi khi export Excel: {str(e)}"
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
            },
            {
                "name": "export_to_excel",
                "description": "Xuất danh sách hóa đơn ra file Excel với các tùy chọn filter",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filter_type": {
                            "type": "string", 
                            "description": "Loại filter: 'all' (tất cả), 'today' (hôm nay), 'date_range' (khoảng thời gian), 'type' (theo loại)",
                            "enum": ["all", "today", "date_range", "type"]
                        },
                        "start_date": {"type": "string", "description": "Ngày bắt đầu (YYYY-MM-DD) - chỉ dùng với date_range"},
                        "end_date": {"type": "string", "description": "Ngày kết thúc (YYYY-MM-DD) - chỉ dùng với date_range"},
                        "invoice_type": {"type": "string", "description": "Loại hóa đơn - chỉ dùng với type filter"}
                    },
                    "required": ["filter_type"]
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
        elif tool_name == "export_to_excel":
            return self.export_to_excel(**kwargs)
        else:
            return {
                "success": False,
                "error": f"Tool {tool_name} not found"
            }
    


