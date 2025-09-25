import random
import re
import requests
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from config import Config
from models.ai_model import AIModel
from utils.text_processor import TextProcessor
# from utils.training_client import TrainingDataClient, InvoicePatternMatcher
import logging

logger = logging.getLogger(__name__)

class ChatHandler:
    def __init__(self):
        self.ai_model = AIModel()
        self.text_processor = TextProcessor()
        self.conversation_history = {}
        
        # Rasa integration
        self.rasa_url = os.getenv('RASA_URL', 'http://rasa:5005')  # Từ environment
        self.use_rasa = True  # Flag để bật/tắt Rasa
        
        # TODO: Re-enable training client after fixing dependency issues
        # Khởi tạo training client để lấy dữ liệu học từ templates
        # self.training_client = TrainingDataClient()
        # self.pattern_matcher = InvoicePatternMatcher(self.training_client)
        self.training_client = None
        self.pattern_matcher = None
        
        # TODO: Re-enable after fixing
        # Kiểm tra kết nối với backend training data
        # if self.training_client and self.training_client.check_health():
        #     logger.info("Kết nối thành công với training data backend")
        # else:
        #     logger.warning("Không thể kết nối với training data backend")
        logger.info("Training client temporarily disabled")
        
        # Kiểm tra kết nối Rasa
        if self.check_rasa_connection():
            logger.info("Kết nối thành công với Rasa")
        else:
            logger.warning("Không thể kết nối với Rasa - fallback to patterns")
            self.use_rasa = False
        
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
            'invoice_analysis': [
                r'(phân tích|analyze|extract)',
                r'(đọc hóa đơn|read invoice)',
                r'(nhận dạng|recognize|identify)',
                r'(thông tin hóa đơn|invoice information)'
            ],
            'template_help': [
                r'(mẫu hóa đơn|template)',
                r'(tạo mẫu|create template)',
                r'(thiết kế hóa đơn|design invoice)'
            ],
            'help': [
                r'(help|hỗ trợ|giúp đỡ)',
                r'(hướng dẫn|guide|instruction)',
                r'(làm sao|how to|cách)'
            ],
            'goodbye': [
                r'(tạm biệt|goodbye|bye|see you)',
                r'(cảm ơn|thank you|thanks)',
                r'(kết thúc|end|finish)'
            ]
        }

    async def process_message(self, message: str, user_id: str = 'anonymous') -> Dict[str, Any]:
        """Xử lý tin nhắn từ user với Rasa integration"""
        logger.info(f"Processing message from {user_id}: {message}")
        
        # Nếu Rasa available, dùng Rasa trước
        if self.use_rasa:
            try:
                rasa_response = self.query_rasa(message, user_id)
                if rasa_response and self.is_good_rasa_response(rasa_response):
                    # Rasa đã xử lý tốt
                    response = self.format_rasa_response(rasa_response)
                    self.update_conversation_history(user_id, message, response)
                    return response
                else:
                    # Rasa poor response → fallback to hybrid system
                    return await self.fallback_to_hybrid_system(message, user_id, rasa_response)
            except Exception as e:
                logger.warning(f"Rasa query failed: {e}, falling back to hybrid system")
                return await self.fallback_to_hybrid_system(message, user_id, {})
        
        # Fallback to original pattern-based logic
        try:
            # Lấy context cuộc hội thoại
            context = self.get_conversation_context(user_id)
            
            # Nhận diện intent
            intent = self.detect_intent(message)
            
            # Xử lý theo intent
            response = self.handle_intent(intent, message, context)
            
            # Cập nhật lịch sử hội thoại
            self.update_conversation_history(user_id, message, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                'message': 'Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại.',
                'type': 'text',
                'suggestions': ['Hỗ trợ kỹ thuật', 'Thử lại', 'Liên hệ admin'],
                'timestamp': datetime.now().isoformat()
            }
    
    def detect_intent(self, message: str) -> str:
        """Phát hiện intent từ tin nhắn"""
        message_clean = self.text_processor.clean_text(message.lower())
        
        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_clean, re.IGNORECASE):
                    return intent
        
        return 'general'
    
    def handle_intent(self, intent: str, message: str, context: Dict) -> Dict[str, Any]:
        """Xử lý intent và trả về response"""
        
        if intent == 'greeting':
            return self.handle_greeting()
        elif intent == 'invoice_query':
            return self.handle_invoice_query(message, context)
        elif intent == 'invoice_analysis':
            return self.handle_invoice_analysis(message, context)
        elif intent == 'template_help':
            return self.handle_template_help(message, context)
        elif intent == 'help':
            return self.handle_help_request()
        elif intent == 'goodbye':
            return self.handle_goodbye()
        else:
            return self.handle_general_query(message, context)
    
    def handle_greeting(self) -> Dict[str, Any]:
        """Xử lý lời chào"""
        greeting_messages = [
            f"Xin chào! Tôi là {Config.BOT_NAME}, trợ lý AI chuyên về hóa đơn. Tôi có thể giúp gì cho bạn?",
            f"Chào bạn! Rất vui được hỗ trợ bạn về các vấn đề hóa đơn và thuế hôm nay!",
            f"Hello! Tôi là {Config.BOT_NAME}, sẵn sàng hỗ trợ bạn mọi thắc mắc về hóa đơn."
        ]
        
        greeting = random.choice(greeting_messages)
        
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
        """Xử lý câu hỏi về hóa đơn bằng AI"""
        
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
    
    def handle_invoice_analysis(self, message: str, context: Dict) -> Dict[str, Any]:
        """Xử lý yêu cầu phân tích hóa đơn"""
        
        ai_response = self.ai_model.generate_invoice_response(message, context)
        
        return {
            'message': ai_response,
            'type': 'text',
            'suggestions': [
                'Upload file hóa đơn',
                'Hướng dẫn OCR',
                'Xem template có sẵn',
                'Tạo template mới'
            ]
        }
    
    def handle_template_help(self, message: str, context: Dict) -> Dict[str, Any]:
        """Xử lý câu hỏi về template"""
        
        ai_response = self.ai_model.generate_invoice_response(message, context)
        
        return {
            'message': ai_response,
            'type': 'text',
            'suggestions': [
                'Xem danh sách template',
                'Tạo template mới',
                'Sửa template hiện có',
                'Hướng dẫn thiết kế'
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
        """Xử lý câu hỏi chung bằng AI"""
        
        # Phân loại câu hỏi có liên quan đến hóa đơn không
        if self._is_invoice_related(message):
            ai_response = self.ai_model.generate_invoice_response(message, context)
            suggestions = [
                'Tạo hóa đơn mới',
                'Tìm kiếm hóa đơn',
                'Xem báo cáo thuế',
                'Hướng dẫn OCR'
            ]
        else:
            ai_response = self.ai_model.generate_general_response(message, context)
            suggestions = [
                'Hướng dẫn sử dụng hệ thống',
                'Tính năng nào có sẵn?',
                'Cách tạo hóa đơn',
                'Hỗ trợ kỹ thuật'
            ]
        
        # Fallback nếu AI không hoạt động
        if not ai_response:
            ai_response = "Xin lỗi, tôi đang gặp sự cố kỹ thuật. Bạn có thể thử hỏi lại hoặc liên hệ bộ phận hỗ trợ."
        
        return {
            'message': ai_response,
            'type': 'text',
            'suggestions': suggestions
        }
    
    def _is_invoice_related(self, message: str) -> bool:
        """Kiểm tra câu hỏi có liên quan đến hóa đơn không"""
        invoice_keywords = [
            'hóa đơn', 'invoice', 'bill', 'thuế', 'tax', 'vat',
            'thanh toán', 'payment', 'mã số thuế', 'tax code',
            'xuất hóa đơn', 'tạo hóa đơn', 'in hóa đơn',
            'báo cáo thuế', 'khai thuế', 'thuế gtgt'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in invoice_keywords)
    
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
    
    # === RASA INTEGRATION METHODS ===
    
    def check_rasa_connection(self) -> bool:
        """Kiểm tra kết nối với Rasa"""
        try:
            response = requests.get(f"{self.rasa_url}/status", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Cannot connect to Rasa: {e}")
            return False
    
    def query_rasa(self, message: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Gửi tin nhắn tới Rasa"""
        try:
            # 1. Webhook để lấy response
            webhook_payload = {"sender": user_id, "message": message}
            webhook_response = requests.post(
                f"{self.rasa_url}/webhooks/rest/webhook",
                json=webhook_payload,
                timeout=10
            )
            
            # 2. Parse để lấy intent/entities
            parse_payload = {"text": message}
            parse_response = requests.post(
                f"{self.rasa_url}/model/parse",
                json=parse_payload,
                timeout=10
            )
            
            if webhook_response.status_code == 200 and parse_response.status_code == 200:
                webhook_data = webhook_response.json()
                parse_data = parse_response.json()
                
                return {
                    'responses': webhook_data,
                    'intent': parse_data.get('intent', {}),
                    'entities': parse_data.get('entities', []),
                    'success': True
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Rasa query error: {e}")
            return None
    
    def is_good_rasa_response(self, rasa_result: Dict[str, Any]) -> bool:
        """Kiểm tra chất lượng response từ Rasa - Enhanced version"""
        if not rasa_result.get('success'):
            return False
            
        responses = rasa_result.get('responses', [])
        if not responses:
            return False
            
        # Kiểm tra confidence - Stricter
        intent = rasa_result.get('intent', {})
        confidence = intent.get('confidence', 0.0)
        
        if confidence < 0.5:  # Tăng từ 0.3 → 0.5
            logger.debug(f"Rasa confidence too low: {confidence:.3f}")
            return False
            
        # Kiểm tra response content
        response_text = responses[0].get('text', '').lower()
        
        # Enhanced bad patterns
        bad_patterns = [
            "xin lỗi, tôi không hiểu",
            "tôi không biết",
            "tôi không thể hiểu", 
            "utter_default",
            "sorry",
            "tôi cần thêm thông tin",
            "bạn có thể nói rõ hơn không"
        ]
        
        for bad_pattern in bad_patterns:
            if bad_pattern in response_text:
                logger.debug(f"Rasa response contains bad pattern: {bad_pattern}")
                return False
        
        # Kiểm tra suspicious patterns (có thể đang "bịa")
        suspicious_patterns = [
            "theo tôi hiểu",
            "có lẽ", 
            "tôi nghĩ rằng",
            "dường như",
            "có thể"
        ]
        
        suspicious_count = sum(1 for pattern in suspicious_patterns if pattern in response_text)
        if suspicious_count >= 2:
            logger.debug(f"Rasa response too suspicious: {suspicious_count} patterns")
            return False
        
        # Kiểm tra length - stricter
        if len(response_text.strip()) < 15:  # Tăng từ 10
            logger.debug(f"Rasa response too short: {len(response_text)} chars")
            return False
        
        logger.debug(f"Rasa response accepted: confidence={confidence:.3f}")
        return True
    
    def format_rasa_response(self, rasa_result: Dict[str, Any]) -> Dict[str, Any]:
        """Format response từ Rasa thành format chuẩn"""
        responses = rasa_result.get('responses', [])
        intent = rasa_result.get('intent', {})
        entities = rasa_result.get('entities', [])
        
        main_response = responses[0].get('text', '') if responses else 'Cảm ơn bạn!'
        
        # Tạo suggestions dựa trên intent
        intent_name = intent.get('name', 'unknown')
        suggestions = self.get_rasa_suggestions(intent_name)
        
        return {
            'message': main_response,
            'type': 'text',
            'method': 'rasa',
            'intent': intent_name,
            'confidence': intent.get('confidence', 0.0),
            'entities': entities,
            'suggestions': suggestions,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_rasa_suggestions(self, intent_name: str) -> List[str]:
        """Tạo suggestions dựa trên Rasa intent"""
        suggestion_map = {
            'greet': ['Tôi cần giúp về hóa đơn', 'Tạo mẫu hóa đơn', 'Upload file'],
            'ask_invoice_help': ['Tạo hóa đơn mới', 'Xem mẫu có sẵn', 'Hướng dẫn OCR'],
            'create_invoice_template': ['Chọn loại mẫu', 'Thêm field', 'Preview mẫu'],
            'extract_invoice_data': ['Upload PDF', 'Upload ảnh', 'Xem kết quả'],
            'goodbye': ['Cảm ơn!', 'Hẹn gặp lại!'],
            'unknown': ['Hướng dẫn', 'Tính năng', 'Hỗ trợ']
        }
        
        return suggestion_map.get(intent_name, ['Tạo hóa đơn', 'OCR', 'Tìm kiếm', 'Hỗ trợ'])
    
    async def fallback_to_hybrid_system(self, message: str, user_id: str, rasa_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback sang Hybrid System khi Rasa không trả lời được
        """
        try:
            # Import hybrid chat handler
            from handlers.hybrid_chat_handler import HybridChatBot
            
            logger.info(f"Falling back to Hybrid System for user {user_id}")
            
            # Khởi tạo hybrid system
            hybrid_chat = HybridChatBot()
            
            # Sử dụng hybrid system để xử lý tin nhắn
            hybrid_response = await hybrid_chat.process_message(message, user_id)
            
            # Enhance response với info về fallback
            if isinstance(hybrid_response, dict):
                hybrid_response['method'] = f"hybrid_fallback_{hybrid_response.get('method', 'unknown')}"
                hybrid_response['fallback_reason'] = "rasa_failed_or_poor_response"
                if rasa_result:
                    hybrid_response['rasa_context'] = rasa_result
                
                self.update_conversation_history(user_id, message, hybrid_response)
                return hybrid_response
            else:
                # Fallback to pattern-based logic nếu hybrid cũng fail
                return self.pattern_based_fallback(message, user_id)
                
        except Exception as e:
            logger.error(f"Hybrid system fallback failed: {str(e)}")
            # Ultimate fallback to pattern-based logic
            return self.pattern_based_fallback(message, user_id)
    
    def pattern_based_fallback(self, message: str, user_id: str) -> Dict[str, Any]:
        """
        Pattern-based fallback logic (original logic)
        """
        try:
            # Lấy context cuộc hội thoại
            context = self.get_conversation_context(user_id)
            
            # Nhận diện intent
            intent = self.detect_intent(message)
            
            # Xử lý theo intent
            response = self.handle_intent(intent, message, context)
            response['method'] = 'pattern_based_fallback'
            response['fallback_reason'] = 'hybrid_system_failed'
            
            # Cập nhật lịch sử hội thoại
            self.update_conversation_history(user_id, message, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Pattern-based fallback error: {str(e)}")
            return {
                'message': 'Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại hoặc liên hệ hỗ trợ.',
                'type': 'text',
                'method': 'simple_fallback',
                'error': str(e),
                'suggestions': ['Hỗ trợ kỹ thuật', 'Thử lại', 'Liên hệ admin'],
                'timestamp': datetime.now().isoformat()
            }