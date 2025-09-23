import random
import re
from datetime import datetime
from typing import Dict, List, Any
from config import Config
from models.ai_model import AIModel
from utils.text_processor import TextProcessor
from utils.training_client import TrainingDataClient, InvoicePatternMatcher
import logging

logger = logging.getLogger(__name__)

class ChatHandler:
    def __init__(self):
        self.ai_model = AIModel()
        self.text_processor = TextProcessor()
        self.conversation_history = {}
        
        # Khởi tạo training client để lấy dữ liệu học từ templates
        self.training_client = TrainingDataClient()
        self.pattern_matcher = InvoicePatternMatcher(self.training_client)
        
        # Kiểm tra kết nối với backend training data
        if self.training_client.check_health():
            logger.info("Kết nối thành công với training data backend")
        else:
            logger.warning("Không thể kết nối với training data backend")
        
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
                r'(loại mẫu|template type)',
                r'(field|trường thông tin)'
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
            'uptime': datetime.now().isoformat(),
            'training_data_status': 'connected' if self.training_client.check_health() else 'disconnected'
        }
    
    def handle_invoice_analysis(self, message: str, context: Dict) -> Dict[str, Any]:
        """Xử lý phân tích hóa đơn sử dụng training data"""
        try:
            # Extract thông tin từ message sử dụng patterns đã học
            extracted_info = self.pattern_matcher.extract_invoice_info(message)
            
            if not extracted_info:
                return {
                    'message': '🔍 Tôi không tìm thấy thông tin hóa đơn rõ ràng trong tin nhắn của bạn.\n\n'
                              'Vui lòng cung cấp thêm thông tin như:\n'
                              '• Số hóa đơn\n'
                              '• Ngày hóa đơn\n'
                              '• Tên công ty\n'
                              '• Số tiền\n'
                              '• Mã số thuế',
                    'type': 'text',
                    'suggestions': [
                        'Gửi ảnh hóa đơn',
                        'Nhập thông tin chi tiết',
                        'Hướng dẫn sử dụng',
                        'Liên hệ hỗ trợ'
                    ]
                }
            
            # Format kết quả
            response_parts = ['🎯 **Thông tin hóa đơn đã nhận dạng:**\n']
            
            for field_name, info in extracted_info.items():
                best_match = info.get('best_match')
                confidence = info.get('confidence', 0.0)
                
                if best_match and confidence > 0.3:  # Chỉ hiển thị nếu độ tin cậy > 30%
                    confidence_icon = '🟢' if confidence > 0.7 else '🟡' if confidence > 0.5 else '🔴'
                    field_display_name = self._get_field_display_name(field_name)
                    
                    response_parts.append(
                        f'{confidence_icon} **{field_display_name}**: {best_match} '
                        f'(Độ tin cậy: {confidence:.0%})'
                    )
            
            # Gợi ý loại template
            suggested_type = self.pattern_matcher.suggest_template_type(extracted_info)
            if suggested_type != 'unknown':
                response_parts.append(f'\n💡 **Loại mẫu gợi ý**: {suggested_type.upper()}')
            
            # Thống kê training data
            stats = self.training_client.get_statistics()
            if stats:
                total_records = stats.get('total_records', 0)
                response_parts.append(f'\n📊 Dựa trên {total_records} mẫu hóa đơn đã học')
            
            return {
                'message': '\n'.join(response_parts),
                'type': 'markdown',
                'extracted_data': extracted_info,
                'suggestions': [
                    'Tạo hóa đơn từ thông tin này',
                    'Kiểm tra thông tin khác',
                    'Xuất file Excel',
                    'Lưu vào hệ thống'
                ]
            }
            
        except Exception as e:
            logger.error(f"Lỗi khi phân tích hóa đơn: {str(e)}")
            return {
                'message': '❌ Có lỗi xảy ra khi phân tích hóa đơn. Vui lòng thử lại sau.',
                'type': 'text',
                'suggestions': ['Thử lại', 'Liên hệ hỗ trợ']
            }
    
    def handle_template_help(self, message: str, context: Dict) -> Dict[str, Any]:
        """Xử lý trợ giúp về templates dựa trên training data"""
        try:
            # Lấy thống kê về templates
            stats = self.training_client.get_statistics()
            
            if not stats:
                return {
                    'message': '📋 **Hỗ trợ về mẫu hóa đơn**\n\n'
                              'Tôi có thể giúp bạn tạo và quản lý các mẫu hóa đơn. '
                              'Tuy nhiên, hiện tại không thể kết nối với dữ liệu mẫu.',
                    'type': 'markdown',
                    'suggestions': ['Thử lại', 'Liên hệ hỗ trợ']
                }
            
            response_parts = ['📋 **Thống kê mẫu hóa đơn trong hệ thống:**\n']
            
            # Hiển thị thống kê theo loại
            by_type = stats.get('by_type', {})
            total_records = stats.get('total_records', 0)
            
            response_parts.append(f'📊 **Tổng số mẫu**: {total_records}')
            
            if by_type:
                response_parts.append('\n**Phân loại theo định dạng:**')
                for template_type, type_stats in by_type.items():
                    count = type_stats.get('count', 0)
                    avg_fields = type_stats.get('avg_fields', 0)
                    response_parts.append(
                        f'• **{template_type.upper()}**: {count} mẫu '
                        f'(TB {avg_fields} trường thông tin)'
                    )
            
            # Gợi ý field phổ biến
            common_fields = self.pattern_matcher.common_fields[:10]
            if common_fields:
                response_parts.append('\n**🏷️ Trường thông tin phổ biến:**')
                for field in common_fields:
                    display_name = self._get_field_display_name(field)
                    response_parts.append(f'• {display_name}')
            
            return {
                'message': '\n'.join(response_parts),
                'type': 'markdown',
                'training_stats': stats,
                'suggestions': [
                    'Tạo mẫu mới',
                    'Xem danh sách mẫu',
                    'Hướng dẫn tạo mẫu',
                    'Nhập mẫu từ file'
                ]
            }
            
        except Exception as e:
            logger.error(f"Lỗi khi xử lý template help: {str(e)}")
            return {
                'message': '❌ Có lỗi xảy ra khi truy xuất thông tin mẫu. Vui lòng thử lại sau.',
                'type': 'text',
                'suggestions': ['Thử lại', 'Liên hệ hỗ trợ']
            }
    
    def _get_field_display_name(self, field_name: str) -> str:
        """Chuyển đổi field name thành tên hiển thị tiếng Việt"""
        display_names = {
            'invoice_number': 'Số hóa đơn',
            'invoice_date': 'Ngày hóa đơn',
            'due_date': 'Hạn thanh toán',
            'company_name': 'Tên công ty',
            'company_address': 'Địa chỉ công ty',
            'tax_code': 'Mã số thuế',
            'customer_name': 'Tên khách hàng',
            'customer_address': 'Địa chỉ khách hàng',
            'customer_phone': 'Điện thoại khách hàng',
            'subtotal': 'Tiền hàng',
            'tax_amount': 'Tiền thuế',
            'total_amount': 'Tổng tiền',
            'amount': 'Số tiền',
            'description': 'Mô tả',
            'quantity': 'Số lượng',
            'unit_price': 'Đơn giá',
            'currency': 'Đơn vị tiền tệ'
        }
        
        return display_names.get(field_name, field_name.replace('_', ' ').title())
    
    def refresh_training_data(self):
        """Refresh training data từ backend"""
        try:
            self.pattern_matcher.refresh_patterns()
            logger.info("Đã refresh training data thành công")
            return True
        except Exception as e:
            logger.error(f"Lỗi khi refresh training data: {str(e)}")
            return False