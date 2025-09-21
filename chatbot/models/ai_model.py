import openai
import json
from typing import Dict, List, Any, Optional
from config import Config

class AIModel:
    def __init__(self):
        openai.api_key = Config.OPENAI_API_KEY
        self.model = Config.DEFAULT_MODEL
        self.max_tokens = Config.MAX_TOKENS
        self.temperature = Config.TEMPERATURE
        
        # System prompts cho các loại câu hỏi khác nhau
        self.system_prompts = {
            'invoice': """
Bạn là trợ lý AI chuyên về hóa đơn và thuế tại Việt Nam.
Nhiệm vụ: Trả lời các câu hỏi về hóa đơn, thuế VAT, quy định pháp luật.
Phong cách: Chuyên nghiệp, thân thiện, cung cấp thông tin chính xác.
Ngôn ngữ: Tiếng Việt.

Kiến thức chuyên môn:
- Luật thuế Việt Nam
- Quy định về hóa đơn điện tử
- Cách tính thuế VAT
- Báo cáo thuế
- Kế toán doanh nghiệp
            """,
            'general': """
Bạn là trợ lý AI thân thiện và hữu ích.
Nhiệm vụ: Trả lời các câu hỏi chung, hỗ trợ người dùng.
Phong cách: Thân thiện, nhiệt tình, tích cực.
Ngôn ngữ: Tiếng Việt.

Nếu không biết câu trả lời, hãy thành thật nói không biết và đề xuất cách khác để hỗ trợ.
            """
        }
    
    def generate_invoice_response(self, message: str, context: Dict) -> str:
        """Tạo phản hồi cho câu hỏi về hóa đơn"""
        try:
            # Lấy lịch sử hội thoại để có context
            conversation_history = self._format_conversation_history(context)
            
            messages = [
                {"role": "system", "content": self.system_prompts['invoice']},
                *conversation_history,
                {"role": "user", "content": message}
            ]
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return self._get_fallback_invoice_response(message)
    
    def generate_general_response(self, message: str, context: Dict) -> str:
        """Tạo phản hồi cho câu hỏi chung"""
        try:
            conversation_history = self._format_conversation_history(context)
            
            messages = [
                {"role": "system", "content": self.system_prompts['general']},
                *conversation_history,
                {"role": "user", "content": message}
            ]
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return self._get_fallback_general_response()
    
    def analyze_invoice_image(self, image_path: str) -> Dict[str, Any]:
        """Phân tích ảnh hóa đơn bằng AI"""
        try:
            # TODO: Implement image analysis with OpenAI Vision API
            # Tạm thời trả về mock data
            return {
                "invoice_number": "HD123456",
                "date": "2025-01-15",
                "company_name": "CÔNG TY ABC",
                "total_amount": "1,000,000",
                "vat_amount": "100,000",
                "confidence": 0.95
            }
        except Exception as e:
            return {"error": f"Không thể phân tích ảnh: {str(e)}"}
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Trích xuất các thực thể từ text"""
        try:
            prompt = f"""
Phân tích văn bản sau và trích xuất các thông tin:
- Số hóa đơn
- Ngày tháng
- Tên công ty
- Số tiền
- Mã số thuế

Văn bản: {text}

Trả về kết quả dạng JSON với các key: invoice_numbers, dates, companies, amounts, tax_codes
            """
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            return json.loads(result)
            
        except Exception as e:
            return {"error": f"Không thể trích xuất thông tin: {str(e)}"}
    
    def _format_conversation_history(self, context: Dict) -> List[Dict]:
        """Format lịch sử hội thoại cho OpenAI API"""
        if not context or 'messages' not in context:
            return []
        
        formatted_history = []
        # Lấy 10 tin nhắn gần nhất để làm context
        recent_messages = context['messages'][-10:]
        
        for msg in recent_messages:
            formatted_history.extend([
                {"role": "user", "content": msg.get('user', '')},
                {"role": "assistant", "content": msg.get('bot', '')}
            ])
        
        return formatted_history
    
    def _get_fallback_invoice_response(self, message: str) -> str:
        """Phản hồi dự phòng cho câu hỏi về hóa đơn"""
        fallback_responses = {
            'tạo hóa đơn': """
Để tạo hóa đơn, bạn có thể:

1. **Tạo hóa đơn thủ công:**
   - Vào mục "Tạo mẫu hóa đơn"
   - Điền thông tin công ty và khách hàng
   - Nhập chi tiết hàng hóa/dịch vụ
   - Hệ thống sẽ tự động tính thuế

2. **Sử dụng template có sẵn:**
   - Chọn mẫu hóa đơn phù hợp
   - Điều chỉnh thông tin cần thiết
   - Xuất file Word hoặc PDF

Bạn cần hỗ trợ thêm về bước nào không?
            """,
            'thuế vat': """
**Thuế VAT tại Việt Nam:**

📊 **Mức thuế suất:**
- 0%: Hàng xuất khẩu, một số dịch vụ
- 5%: Hàng thiết yếu (gạo, thuốc, sách...)
- 10%: Mức thuế suất tiêu chuẩn
- Không chịu thuế: Một số dịch vụ đặc biệt

💡 **Cách tính:**
- Thuế VAT = Giá chưa thuế × Thuế suất
- Giá đã thuế = Giá chưa thuế + Thuế VAT

Bạn cần tôi tính cụ thể cho trường hợp nào không?
            """,
            'mã số thuế': """
**Mã số thuế doanh nghiệp:**

🔢 **Cấu trúc:** 10 chữ số hoặc 13 chữ số
- 10 số: Doanh nghiệp chính
- 13 số: Chi nhánh (10 số + 3 số chi nhánh)

📋 **Cách tra cứu:**
- Website: thuetncn.gdt.gov.vn
- Ứng dụng iTax
- Liên hệ Chi cục thuế

⚠️ **Lưu ý:** MST phải chính xác trên hóa đơn để hợp lệ.

Bạn cần tra cứu MST cụ thể nào không?
            """
        }
        
        message_lower = message.lower()
        for key, response in fallback_responses.items():
            if key in message_lower:
                return response.strip()
        
        return """
Tôi hiểu bạn đang hỏi về hóa đơn. Có thể bạn muốn biết về:

• 📄 Cách tạo hóa đơn mới
• 🔍 Tìm kiếm hóa đơn đã tạo
• 📊 Báo cáo thuế và thống kê
• ⚖️ Quy định pháp luật về hóa đơn
• 💰 Cách tính thuế VAT

Bạn có thể hỏi cụ thể hơn để tôi hỗ trợ tốt nhất!
        """.strip()
    
    def _get_fallback_general_response(self) -> str:
        """Phản hồi dự phòng cho câu hỏi chung"""
        return """
Xin lỗi, tôi gặp một chút khó khăn trong việc xử lý câu hỏi của bạn.

Tôi có thể hỗ trợ bạn về:
• 📄 Quản lý hóa đơn
• 📊 Báo cáo thuế
• 🔍 Tìm kiếm thông tin
• 💡 Tư vấn quy định

Bạn có thể hỏi lại hoặc liên hệ bộ phận hỗ trợ để được giúp đỡ!
        """.strip()