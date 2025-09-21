import random
import re
from datetime import datetime
from typing import Dict, List, Any
from config import Config
from models.ai_model import AIModel
from utils.text_processor import TextProcessor

class ChatHandler:
    def __init__(self):
        self.ai_model = AIModel()
        self.text_processor = TextProcessor()
        self.conversation_history = {}
        
        # Patterns cho nhận diện intent
        self.patterns = {
            'greeting': [
                r'(xin chào|chào|hello|hi|hey)',
                r'(good morning|good afternoon|good evening)',
                r'(chào buổi sáng|chào buổi chiều|chào buổi tối)'
            ],
            'invoice_query': [
                r'(hóa đơn|invoice|bill)',
                r'(mã số thuế|tax code)',
                r'(thanh toán|payment)',
                r'(VAT|thuế giá trị gia tăng)'
            ],
            'help': [
                r'(giúp|help|hỗ trợ|support)',
                r'(làm thế nào|how to|cách)',
                r'(có thể|can you|bạn có thể)'
            ],
            'goodbye': [
                r'(tạm biệt|goodbye|bye|see you)',
                r'(cảm ơn|thank you|thanks)',
                r'(kết thúc|end|quit)'
            ]
        }
    
    def process_message(self, message: str, user_id: str) -> Dict[str, Any]:
        """Xử lý tin nhắn từ user"""
        
        # Normalize text
        processed_message = self.text_processor.normalize(message)
        
        # Detect intent
        intent = self.detect_intent(processed_message)
        
        # Get conversation context
        context = self.get_conversation_context(user_id)
        
        # Generate response based on intent
        response = self.generate_response(intent, processed_message, context)
        
        # Update conversation history
        self.update_conversation_history(user_id, message, response)
        
        return response
    
    def detect_intent(self, message: str) -> str:
        """Nhận diện ý định của user"""
        message_lower = message.lower()
        
        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return intent
        
        return 'general'
    
    def generate_response(self, intent: str, message: str, context: Dict) -> Dict[str, Any]:
        """Tạo phản hồi dựa trên intent"""
        
        if intent == 'greeting':
            return self.handle_greeting()
        elif intent == 'invoice_query':
            return self.handle_invoice_query(message, context)
        elif intent == 'help':
            return self.handle_help_request()
        elif intent == 'goodbye':
            return self.handle_goodbye()
        else:
            return self.handle_general_query(message, context)
    
    def handle_greeting(self) -> Dict[str, Any]:
        """Xử lý lời chào"""
        greeting = random.choice(Config.GREETING_MESSAGES).format(
            bot_name=Config.BOT_NAME
        )
        
        return {
            'message': greeting,
            'type': 'text',
            'suggestions': [
                'Tôi muốn tìm hiểu về hóa đơn',
                'Làm thế nào để tạo hóa đơn?',
                'Kiểm tra thông tin thuế',
                'Hướng dẫn sử dụng hệ thống'
            ]
        }
    
    def handle_invoice_query(self, message: str, context: Dict) -> Dict[str, Any]:
        """Xử lý câu hỏi về hóa đơn"""
        
        # Sử dụng AI để phân tích và trả lời
        ai_response = self.ai_model.generate_invoice_response(message, context)
        
        return {
            'message': ai_response,
            'type': 'text',
            'suggestions': [
                'Tạo hóa đơn mới',
                'Tìm kiếm hóa đơn',
                'Xuất báo cáo',
                'Hỗ trợ khác'
            ]
        }
    
    def handle_help_request(self) -> Dict[str, Any]:
        """Xử lý yêu cầu trợ giúp"""
        help_message = f"""
🤖 **{Config.BOT_NAME}** - Trợ lý AI của bạn

**Tôi có thể giúp bạn:**
• 📄 Tạo và quản lý hóa đơn
• 🔍 Tìm kiếm thông tin hóa đơn
• 📊 Tạo báo cáo thuế
• 💡 Tư vấn về quy định thuế
• 🆘 Hỗ trợ kỹ thuật

**Cách sử dụng:**
- Hỏi trực tiếp về vấn đề bạn cần hỗ trợ
- Gửi ảnh hóa đơn để tôi phân tích
- Yêu cầu tạo báo cáo cụ thể

Bạn cần hỗ trợ gì hôm nay?
        """
        
        return {
            'message': help_message.strip(),
            'type': 'markdown',
            'suggestions': [
                'Hướng dẫn tạo hóa đơn',
                'Cách tính thuế VAT',
                'Xuất dữ liệu Excel',
                'Liên hệ hỗ trợ'
            ]
        }
    
    def handle_goodbye(self) -> Dict[str, Any]:
        """Xử lý lời tạm biệt"""
        goodbye_messages = [
            "Cảm ơn bạn đã sử dụng dịch vụ! Hẹn gặp lại! 👋",
            "Rất vui được hỗ trợ bạn. Chúc bạn một ngày tốt lành! 😊",
            "Tạm biệt! Liên hệ tôi bất cứ khi nào bạn cần hỗ trợ! 🚀"
        ]
        
        return {
            'message': random.choice(goodbye_messages),
            'type': 'text',
            'suggestions': []
        }
    
    def handle_general_query(self, message: str, context: Dict) -> Dict[str, Any]:
        """Xử lý câu hỏi chung"""
        
        # Sử dụng AI để trả lời
        ai_response = self.ai_model.generate_general_response(message, context)
        
        if not ai_response:
            error_message = random.choice(Config.ERROR_MESSAGES)
            return {
                'message': error_message,
                'type': 'text',
                'suggestions': [
                    'Hỏi về hóa đơn',
                    'Cần hỗ trợ',
                    'Hướng dẫn sử dụng',
                    'Liên hệ admin'
                ]
            }
        
        return {
            'message': ai_response,
            'type': 'text',
            'suggestions': [
                'Tiếp tục hỏi',
                'Cần hỗ trợ khác',
                'Kết thúc',
                'Đánh giá dịch vụ'
            ]
        }
    
    def get_conversation_context(self, user_id: str) -> Dict:
        """Lấy ngữ cảnh cuộc hội thoại"""
        return self.conversation_history.get(user_id, {
            'messages': [],
            'started_at': datetime.now(),
            'last_intent': None
        })
    
    def update_conversation_history(self, user_id: str, user_message: str, bot_response: Dict):
        """Cập nhật lịch sử hội thoại"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = {
                'messages': [],
                'started_at': datetime.now(),
                'last_intent': None
            }
        
        self.conversation_history[user_id]['messages'].append({
            'user': user_message,
            'bot': bot_response['message'],
            'timestamp': datetime.now(),
            'type': bot_response.get('type', 'text')
        })
        
        # Giữ chỉ 50 tin nhắn gần nhất
        if len(self.conversation_history[user_id]['messages']) > 50:
            self.conversation_history[user_id]['messages'] = \
                self.conversation_history[user_id]['messages'][-50:]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Lấy thống kê chatbot"""
        total_users = len(self.conversation_history)
        total_messages = sum(
            len(history['messages']) 
            for history in self.conversation_history.values()
        )
        
        return {
            'total_users': total_users,
            'total_messages': total_messages,
            'active_conversations': total_users,
            'uptime': datetime.now().isoformat()
        }