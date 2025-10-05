import google.generativeai as genai
import os
from typing import Optional, Dict, List, Any
import json
import sys

# Import config
try:
    from config import Config
except ImportError:
    # Fallback for relative import issues
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from config import Config

class GoogleAIService:
    def __init__(self):
        """Initialize Google AI Service"""
        self.api_key = Config.GOOGLE_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
            
    def is_available(self) -> bool:
        """Check if Google AI service is available"""
        return self.model is not None and self.api_key
    
    def generate_response(self, prompt: str) -> Optional[str]:
        """
        Generate response from Google AI with custom prompt
        
        Args:
            prompt: Full prompt with context
            
        Returns:
            AI response or None if service unavailable
        """
        if not self.is_available():
            return None
            
        try:
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            print(f"Google AI Error: {e}")
            return None
    
    def enhance_database_query(self, user_message: str, database_context: Dict) -> Optional[str]:
        """
        Enhance database understanding using Google AI
        
        Args:
            user_message: User's natural language query
            database_context: Context from database (recent invoices, patterns, etc.)
            
        Returns:
            Enhanced response or None if service unavailable
        """
        if not self.is_available():
            return None
            
        try:
            # Prepare context for AI
            context_prompt = self._build_database_context_prompt(database_context)
            
            prompt = f"""
Bạn là trợ lý AI chuyên về xử lý hóa đơn và database. Dựa vào thông tin database sau:

{context_prompt}

Hãy trả lời câu hỏi của người dùng một cách chi tiết và hữu ích:
"{user_message}"

Yêu cầu:
- Trả lời bằng tiếng Việt
- Sử dụng thông tin cụ thể từ database
- Đưa ra phân tích và insight có ý nghĩa
- Nếu không có dữ liệu phù hợp, hãy gợi ý cách tìm kiếm khác
"""

            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            print(f"Google AI Error: {e}")
            return None
    
    def analyze_invoice_patterns(self, invoices_data: List[Dict]) -> Optional[str]:
        """
        Analyze invoice patterns using Google AI
        
        Args:
            invoices_data: List of invoice data
            
        Returns:
            Analysis result or None if service unavailable
        """
        if not self.is_available() or not invoices_data:
            return None
            
        try:
            # Summarize invoice data for AI analysis
            summary = self._summarize_invoices(invoices_data)
            
            prompt = f"""
Phân tích dữ liệu hóa đơn sau và đưa ra insights:

{summary}

Hãy phân tích:
1. Xu hướng theo loại hóa đơn
2. Patterns trong dữ liệu khách hàng
3. Thông tin về mức sử dụng (nếu có)
4. Các điểm bất thường hoặc đáng chú ý
5. Gợi ý cải thiện quy trình

Trả lời bằng tiếng Việt với format dễ đọc.
"""

            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            print(f"Google AI Analysis Error: {e}")
            return None
    
    def smart_search_suggestion(self, query: str, available_fields: List[str]) -> Optional[str]:
        """
        Provide smart search suggestions using Google AI
        
        Args:
            query: User's search query
            available_fields: Available database fields
            
        Returns:
            Search suggestions or None if service unavailable
        """
        if not self.is_available():
            return None
            
        try:
            fields_str = ", ".join(available_fields)
            
            prompt = f"""
Người dùng muốn tìm kiếm: "{query}"

Các trường dữ liệu có sẵn trong database: {fields_str}

Hãy gợi ý cách tìm kiếm hiệu quả:
1. Trường nào nên tìm kiếm
2. Từ khóa nào nên sử dụng
3. Cách tối ưu hóa tìm kiếm

Trả lời bằng tiếng Việt, ngắn gọn và hữu ích.
"""

            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            print(f"Google AI Search Suggestion Error: {e}")
            return None
    
    def _build_database_context_prompt(self, context: Dict) -> str:
        """Build context prompt for database queries"""
        context_parts = []
        
        if 'recent_invoices' in context:
            context_parts.append(f"Hóa đơn gần đây: {len(context['recent_invoices'])} hóa đơn")
            
        if 'invoice_types' in context:
            types_str = ", ".join(context['invoice_types'])
            context_parts.append(f"Loại hóa đơn: {types_str}")
            
        if 'total_invoices' in context:
            context_parts.append(f"Tổng số hóa đơn: {context['total_invoices']}")
            
        if 'date_range' in context:
            context_parts.append(f"Khoảng thời gian: {context['date_range']}")
            
        return "\n".join(context_parts) if context_parts else "Không có dữ liệu context"
    
    def _summarize_invoices(self, invoices_data: List[Dict]) -> str:
        """Summarize invoice data for AI analysis"""
        if not invoices_data:
            return "Không có dữ liệu hóa đơn"
        
        summary_parts = [f"Tổng số hóa đơn: {len(invoices_data)}"]
        
        # Count by invoice types
        types_count = {}
        buyers = set()
        
        for invoice in invoices_data:
            invoice_type = invoice.get('invoice_type', 'Unknown')
            types_count[invoice_type] = types_count.get(invoice_type, 0) + 1
            
            if invoice.get('buyer_name'):
                buyers.add(invoice['buyer_name'])
        
        if types_count:
            types_summary = ", ".join([f"{k}: {v}" for k, v in types_count.items()])
            summary_parts.append(f"Phân loại: {types_summary}")
        
        if buyers:
            summary_parts.append(f"Số khách hàng: {len(buyers)}")
        
        return "\n".join(summary_parts)