"""
Rasa Chat Handler
Handler chính để giao tiếp với Rasa, với fallback sang OpenAI khi cần
"""

import requests
import json
import logging
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from models.ai_model import AIModel

logger = logging.getLogger(__name__)

class RasaChatHandler:
    """
    Rasa-first chatbot handler
    
    Flow:
    1. Rasa xử lý tin nhắn trước
    2. Kiểm tra chất lượng response
    3. Nếu không tốt, fallback sang OpenAI với context từ Rasa
    4. Trả về response tốt nhất
    """
    
    def __init__(self):
        self.ai_model = AIModel()
        self.rasa_url = os.getenv('RASA_URL', 'http://rasa:5005')  # Từ environment
        self.conversation_history = {}
        
        # Confidence thresholds
        self.min_confidence = 0.3  # Dưới này sẽ fallback OpenAI
        self.good_confidence = 0.7  # Trên này sẽ dùng Rasa response
        
        # Response quality checks
        self.bad_response_patterns = [
            "xin lỗi, tôi không hiểu",
            "tôi không biết",
            "utter_default",
            "sorry, i didn't get that"
        ]
        
        # System prompts for OpenAI fallback
        self.system_prompts = {
            'invoice_context': """
Bạn là trợ lý AI chuyên về hóa đơn và thuế tại Việt Nam.
Context từ Rasa: Intent={intent}, Entities={entities}, Confidence={confidence}

Dựa trên context này, hãy trả lời câu hỏi của người dùng một cách chuyên nghiệp và chính xác.
Nếu liên quan đến hóa đơn, thuế VAT, kế toán - hãy đưa ra thông tin chi tiết.
Nếu là câu hỏi chung, hãy trả lời thân thiện và hữu ích.

Ngôn ngữ: Tiếng Việt
Phong cách: Chuyên nghiệp, thân thiện, dễ hiểu
            """,
            
            'general_context': """
Bạn là trợ lý AI thân thiện cho hệ thống quản lý hóa đơn.
Context từ Rasa: Intent={intent}, Entities={entities}, Confidence={confidence}

Hãy trả lời câu hỏi dựa trên context này. Nếu Rasa đã xác định được intent/entities,
hãy sử dụng thông tin đó để đưa ra phản hồi phù hợp.

Khả năng của hệ thống:
- Tạo và quản lý mẫu hóa đơn
- OCR trích xuất dữ liệu từ hình ảnh
- Tìm kiếm và phân tích hóa đơn
- Tính toán thuế VAT
- Hỗ trợ upload file PDF/image

Ngôn ngữ: Tiếng Việt
Phong cách: Thân thiện, hữu ích
            """
        }
    
    async def process_message(self, message: str, user_id: str = 'default') -> Dict[str, Any]:
        """
        Xử lý tin nhắn với Rasa-first approach
        """
        try:
            # Step 1: Gửi tin nhắn tới Rasa
            rasa_result = await self.query_rasa(message, user_id)
            
            # Step 2: Đánh giá chất lượng response từ Rasa
            if self.is_good_rasa_response(rasa_result):
                # Rasa đã cho response tốt
                response = self.format_rasa_response(rasa_result, message, user_id)
                logger.info(f"Using Rasa response for user {user_id}")
                
            else:
                # Fallback sang OpenAI với context từ Rasa
                response = await self.fallback_to_openai(message, user_id, rasa_result)
                logger.info(f"Fallback to OpenAI for user {user_id}")
            
            # Step 3: Update conversation history
            self.update_conversation_history(user_id, message, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                'message': 'Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại sau.',
                'type': 'text',
                'method': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def query_rasa(self, message: str, user_id: str) -> Dict[str, Any]:
        """
        Gửi tin nhắn tới Rasa và lấy response + intent/entities
        """
        try:
            # 1. Gửi webhook request để lấy response
            webhook_payload = {
                "sender": user_id,
                "message": message
            }
            
            webhook_response = requests.post(
                f"{self.rasa_url}/webhooks/rest/webhook",
                json=webhook_payload,
                timeout=10
            )
            
            # 2. Gửi parse request để lấy intent/entities
            parse_payload = {
                "text": message
            }
            
            parse_response = requests.post(
                f"{self.rasa_url}/model/parse",
                json=parse_payload,
                timeout=10
            )
            
            # 3. Combine results
            webhook_data = webhook_response.json() if webhook_response.status_code == 200 else []
            parse_data = parse_response.json() if parse_response.status_code == 200 else {}
            
            return {
                'responses': webhook_data,
                'intent': parse_data.get('intent', {}),
                'entities': parse_data.get('entities', []),
                'text': parse_data.get('text', message),
                'success': webhook_response.status_code == 200 and parse_response.status_code == 200
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Rasa request failed: {str(e)}")
            return {
                'responses': [],
                'intent': {'name': 'unknown', 'confidence': 0.0},
                'entities': [],
                'text': message,
                'success': False,
                'error': str(e)
            }
    
    def is_good_rasa_response(self, rasa_result: Dict[str, Any]) -> bool:
        """
        Kiểm tra xem response từ Rasa có tốt không
        """
        if not rasa_result.get('success', False):
            return False
        
        responses = rasa_result.get('responses', [])
        if not responses:
            return False
        
        # Kiểm tra confidence
        intent = rasa_result.get('intent', {})
        confidence = intent.get('confidence', 0.0)
        
        if confidence < self.min_confidence:
            return False
        
        # Kiểm tra response content
        response_text = responses[0].get('text', '').lower()
        
        # Check for bad patterns
        for bad_pattern in self.bad_response_patterns:
            if bad_pattern in response_text:
                return False
        
        # Check response length (too short might be generic)
        if len(response_text.strip()) < 10:
            return False
        
        return True
    
    def format_rasa_response(self, rasa_result: Dict[str, Any], original_message: str, user_id: str) -> Dict[str, Any]:
        """
        Format response từ Rasa thành format chuẩn
        """
        responses = rasa_result.get('responses', [])
        intent = rasa_result.get('intent', {})
        entities = rasa_result.get('entities', [])
        
        # Lấy response chính từ Rasa
        main_response = responses[0].get('text', '') if responses else 'Cảm ơn bạn đã liên hệ!'
        
        # Enhance với thông tin từ entities nếu có
        if entities:
            main_response = self.enhance_with_entities(main_response, entities)
        
        # Tạo suggestions dựa trên intent
        suggestions = self.get_intent_suggestions(intent.get('name', 'unknown'))
        
        return {
            'message': main_response,
            'type': 'text',
            'method': 'rasa',
            'intent': intent.get('name', 'unknown'),
            'confidence': intent.get('confidence', 0.0),
            'entities': entities,
            'suggestions': suggestions,
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'original_message': original_message,
            'rasa_buttons': responses[0].get('buttons', []) if responses else [],
            'rasa_custom': responses[0].get('custom', {}) if responses else {}
        }
    
    async def fallback_to_openai(self, message: str, user_id: str, rasa_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback sang OpenAI với context từ Rasa
        """
        try:
            intent = rasa_result.get('intent', {})
            entities = rasa_result.get('entities', [])
            intent_name = intent.get('name', 'unknown')
            confidence = intent.get('confidence', 0.0)
            
            # Chọn system prompt phù hợp
            if any(keyword in intent_name.lower() for keyword in ['invoice', 'template', 'ocr', 'tax']):
                system_prompt = self.system_prompts['invoice_context']
            else:
                system_prompt = self.system_prompts['general_context']
            
            # Format system prompt với context
            formatted_prompt = system_prompt.format(
                intent=intent_name,
                entities=entities,
                confidence=confidence
            )
            
            # Lấy conversation history
            history = self.get_conversation_history(user_id)
            
            # Gọi OpenAI API
            messages = [{"role": "system", "content": formatted_prompt}]
            messages.extend(history)
            messages.append({"role": "user", "content": message})
            
            response = self.ai_model.client.chat.completions.create(
                model=self.ai_model.model,
                messages=messages,
                max_tokens=self.ai_model.max_tokens,
                temperature=self.ai_model.temperature
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Tạo suggestions
            suggestions = self.get_intent_suggestions(intent_name)
            
            return {
                'message': ai_response,
                'type': 'text',
                'method': 'openai_fallback',
                'intent': intent_name,
                'confidence': confidence,
                'entities': entities,
                'suggestions': suggestions,
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'original_message': message,
                'rasa_context': rasa_result
            }
            
        except Exception as e:
            logger.error(f"OpenAI fallback failed: {str(e)}")
            
            # Ultimate fallback - simple response
            return {
                'message': f'Cảm ơn bạn đã hỏi: "{message}". Tôi đang học hỏi để trả lời tốt hơn. Bạn có thể thử hỏi về hóa đơn, mẫu hóa đơn, OCR, hoặc các tính năng khác của hệ thống.',
                'type': 'text',
                'method': 'simple_fallback',
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'suggestions': ['Tạo mẫu hóa đơn', 'Upload file OCR', 'Hướng dẫn sử dụng', 'Hỗ trợ kỹ thuật']
            }
    
    def enhance_with_entities(self, response: str, entities: List[Dict]) -> str:
        """
        Enhance response với thông tin từ entities
        """
        if not entities:
            return response
        
        # Extract useful entity info
        entity_info = []
        for entity in entities:
            entity_value = entity.get('value', '')
            entity_type = entity.get('entity', '')
            
            if entity_value and entity_type:
                entity_info.append(f"{entity_type}: {entity_value}")
        
        if entity_info:
            enhancement = f"\n\n📋 Thông tin nhận dạng: {', '.join(entity_info)}"
            return response + enhancement
        
        return response
    
    def get_intent_suggestions(self, intent_name: str) -> List[str]:
        """
        Tạo suggestions dựa trên intent
        """
        suggestion_map = {
            'greet': ['Tôi cần giúp đỡ về hóa đơn', 'Tạo mẫu hóa đơn', 'Upload file OCR'],
            'ask_invoice_help': ['Tạo hóa đơn mới', 'Xem mẫu có sẵn', 'Hướng dẫn OCR'],
            'create_invoice_template': ['Chọn loại mẫu', 'Thêm field tùy chỉnh', 'Xem preview mẫu'],
            'extract_invoice_data': ['Upload file PDF', 'Upload hình ảnh', 'Xem kết quả OCR'],
            'search_invoice': ['Tìm theo MST', 'Tìm theo ngày', 'Tìm theo số tiền'],
            'ask_template_types': ['Mẫu hóa đơn VAT', 'Mẫu hóa đơn dịch vụ', 'Mẫu hóa đơn hàng hóa'],
            'goodbye': ['Cảm ơn bạn!', 'Hẹn gặp lại!'],
            'unknown': ['Hướng dẫn sử dụng', 'Các tính năng có sẵn', 'Hỗ trợ kỹ thuật', 'FAQ']
        }
        
        return suggestion_map.get(intent_name, ['Tạo hóa đơn', 'OCR file', 'Tìm kiếm', 'Hỗ trợ'])
    
    def update_conversation_history(self, user_id: str, message: str, response: Dict[str, Any]):
        """
        Cập nhật lịch sử conversation
        """
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        # Add user message
        self.conversation_history[user_id].append({
            "role": "user",
            "content": message
        })
        
        # Add bot response
        self.conversation_history[user_id].append({
            "role": "assistant", 
            "content": response.get('message', '')
        })
        
        # Keep only last 10 messages (5 turns)
        if len(self.conversation_history[user_id]) > 10:
            self.conversation_history[user_id] = self.conversation_history[user_id][-10:]
    
    def get_conversation_history(self, user_id: str) -> List[Dict[str, str]]:
        """
        Lấy lịch sử conversation
        """
        return self.conversation_history.get(user_id, [])[-6:]  # Last 3 turns