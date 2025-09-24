"""
Hybrid AI Chatbot System
Kết hợp Rasa NLU + OpenAI API + Custom Invoice Logic
"""

import requests
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from models.ai_model import AIModel
import openai

logger = logging.getLogger(__name__)

class HybridChatBot:
    """
    Hybrid chatbot kết hợp Rasa và OpenAI API
    
    Flow:
    1. Rasa NLU -> Intent classification & Entity extraction
    2. Custom Logic -> Invoice/OCR specific processing 
    3. OpenAI API -> Complex reasoning & knowledge questions
    4. Response fusion -> Best answer selection
    """
    
    def __init__(self):
        self.ai_model = AIModel()
        self.rasa_url = "http://localhost:5005"  # Rasa server
        self.conversation_history = {}
        
        # Intent routing configuration
        self.intent_routing = {
            # Rasa handles these intents
            'rasa_intents': [
                'greet', 'goodbye', 'affirm', 'deny',
                'ask_invoice_help', 'create_invoice_template',
                'extract_invoice_data', 'search_invoice',
                'upload_invoice', 'ask_invoice_format',
                'ask_template_types', 'request_ocr_help'
            ],
            
            # OpenAI handles complex reasoning
            'openai_intents': [
                'complex_question', 'knowledge_query',
                'tax_calculation', 'legal_advice',
                'business_consultation', 'general_chat'
            ],
            
            # Custom logic for invoice processing
            'custom_intents': [
                'process_invoice_file', 'ocr_extraction',
                'template_matching', 'data_validation'
            ]
        }
        
        # System prompts for different contexts
        self.context_prompts = {
            'invoice_expert': """
Bạn là chuyên gia về hóa đơn và thuế tại Việt Nam.
Chuyên môn: Luật thuế, hóa đơn điện tử, VAT, kế toán.
Phong cách: Chuyên nghiệp, chính xác, chi tiết.
Dựa vào context từ Rasa: {rasa_context}
            """,
            
            'general_assistant': """
Bạn là trợ lý AI thân thiện cho hệ thống quản lý hóa đơn.
Nhiệm vụ: Hỗ trợ người dùng, giải đáp thắc mắc.
Phong cách: Thân thiện, hữu ích, dễ hiểu.
Context từ Rasa: {rasa_context}
            """,
            
            'technical_support': """
Bạn là chuyên gia kỹ thuật hỗ trợ hệ thống OCR và AI.
Chuyên môn: OCR, template matching, file processing.
Phong cách: Kỹ thuật nhưng dễ hiểu.
Context: {rasa_context}
            """
        }
    
    async def process_message(self, message: str, user_id: str = 'default') -> Dict[str, Any]:
        """
        Main processing pipeline
        """
        try:
            # Step 1: Rasa NLU Analysis
            rasa_result = await self.analyze_with_rasa(message, user_id)
            
            # Step 2: Intent routing
            processing_method = self.determine_processing_method(rasa_result)
            
            # Step 3: Generate response based on method
            if processing_method == 'rasa':
                response = await self.handle_with_rasa(message, user_id, rasa_result)
            elif processing_method == 'openai':
                response = await self.handle_with_openai(message, user_id, rasa_result)
            elif processing_method == 'custom':
                response = await self.handle_with_custom_logic(message, user_id, rasa_result)
            else:
                # Hybrid approach - combine multiple methods
                response = await self.handle_hybrid(message, user_id, rasa_result)
            
            # Step 4: Update conversation history
            self.update_conversation_history(user_id, message, response, rasa_result)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in hybrid chat processing: {str(e)}")
            return self.create_error_response(str(e))
    
    async def analyze_with_rasa(self, message: str, user_id: str) -> Dict[str, Any]:
        """
        Gửi tin nhắn đến Rasa để phân tích intent và entities
        """
        try:
            rasa_payload = {
                "sender": user_id,
                "message": message
            }
            
            # Parse request để lấy intent và entities
            parse_response = requests.post(
                f"{self.rasa_url}/model/parse",
                json={"text": message}
            )
            
            if parse_response.status_code == 200:
                parse_data = parse_response.json()
                
                # Conversation request để lấy Rasa response
                conv_response = requests.post(
                    f"{self.rasa_url}/webhooks/rest/webhook",
                    json=rasa_payload
                )
                
                conv_data = conv_response.json() if conv_response.status_code == 200 else []
                
                return {
                    'intent': parse_data.get('intent', {}).get('name', 'unknown'),
                    'confidence': parse_data.get('intent', {}).get('confidence', 0.0),
                    'entities': parse_data.get('entities', []),
                    'rasa_responses': conv_data,
                    'success': True
                }
            else:
                logger.warning(f"Rasa parse failed: {parse_response.status_code}")
                return {'success': False, 'error': 'Rasa connection failed'}
                
        except Exception as e:
            logger.error(f"Rasa analysis error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def determine_processing_method(self, rasa_result: Dict) -> str:
        """
        Quyết định method xử lý dựa trên Rasa analysis
        """
        if not rasa_result.get('success', False):
            return 'openai'  # Fallback to OpenAI
        
        intent = rasa_result.get('intent', 'unknown')
        confidence = rasa_result.get('confidence', 0.0)
        
        # High confidence Rasa intents
        if confidence > 0.8 and intent in self.intent_routing['rasa_intents']:
            return 'rasa'
        
        # Custom processing for invoice-specific tasks
        if intent in self.intent_routing['custom_intents']:
            return 'custom'
        
        # Low confidence or complex questions -> OpenAI
        if confidence < 0.5 or intent in self.intent_routing['openai_intents']:
            return 'openai'
        
        # Default hybrid approach
        return 'hybrid'
    
    async def handle_with_rasa(self, message: str, user_id: str, rasa_result: Dict) -> Dict[str, Any]:
        """
        Sử dụng Rasa response làm chính
        """
        rasa_responses = rasa_result.get('rasa_responses', [])
        
        if rasa_responses:
            # Lấy response đầu tiên từ Rasa
            primary_response = rasa_responses[0].get('text', '')
            
            # Enhance với context từ entities
            entities = rasa_result.get('entities', [])
            enhanced_response = self.enhance_rasa_response(primary_response, entities)
            
            return {
                'message': enhanced_response,
                'type': 'text',
                'method': 'rasa',
                'intent': rasa_result.get('intent'),
                'confidence': rasa_result.get('confidence'),
                'entities': entities,
                'suggestions': self.get_intent_based_suggestions(rasa_result.get('intent'))
            }
        else:
            # Fallback to OpenAI if no Rasa response
            return await self.handle_with_openai(message, user_id, rasa_result)
    
    async def handle_with_openai(self, message: str, user_id: str, rasa_result: Dict) -> Dict[str, Any]:
        """
        Sử dụng OpenAI API với context từ Rasa
        """
        # Determine context type
        intent = rasa_result.get('intent', 'general')
        entities = rasa_result.get('entities', [])
        
        # Select appropriate prompt
        if any(keyword in intent for keyword in ['invoice', 'tax', 'template']):
            context_type = 'invoice_expert'
        elif any(keyword in intent for keyword in ['ocr', 'extract', 'upload']):
            context_type = 'technical_support'
        else:
            context_type = 'general_assistant'
        
        # Build context string
        rasa_context = f"Intent: {intent}, Entities: {entities}"
        system_prompt = self.context_prompts[context_type].format(rasa_context=rasa_context)
        
        # Get conversation history
        history = self.get_conversation_context(user_id)
        
        try:
            response = self.ai_model.client.chat.completions.create(
                model=self.ai_model.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *history,
                    {"role": "user", "content": message}
                ],
                max_tokens=self.ai_model.max_tokens,
                temperature=self.ai_model.temperature
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            return {
                'message': ai_response,
                'type': 'text',
                'method': 'openai',
                'intent': intent,
                'confidence': rasa_result.get('confidence', 0.0),
                'entities': entities,
                'suggestions': self.get_intent_based_suggestions(intent)
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return self.create_fallback_response(message, rasa_result)
    
    async def handle_with_custom_logic(self, message: str, user_id: str, rasa_result: Dict) -> Dict[str, Any]:
        """
        Custom logic cho invoice processing
        """
        intent = rasa_result.get('intent', '')
        entities = rasa_result.get('entities', [])
        
        if intent == 'extract_invoice_data':
            return self.handle_invoice_extraction(entities)
        elif intent == 'process_invoice_file':
            return self.handle_file_processing(entities)
        elif intent == 'template_matching':
            return self.handle_template_matching(entities)
        else:
            # Fallback to OpenAI for unknown custom intents
            return await self.handle_with_openai(message, user_id, rasa_result)
    
    async def handle_hybrid(self, message: str, user_id: str, rasa_result: Dict) -> Dict[str, Any]:
        """
        Kết hợp Rasa structure + OpenAI content
        """
        # Get Rasa structure
        rasa_response = await self.handle_with_rasa(message, user_id, rasa_result)
        
        # Enhance with OpenAI if needed
        if rasa_result.get('confidence', 0) < 0.7:
            openai_response = await self.handle_with_openai(message, user_id, rasa_result)
            
            # Combine responses intelligently
            combined_message = self.combine_responses(rasa_response, openai_response)
            
            return {
                'message': combined_message,
                'type': 'text',
                'method': 'hybrid',
                'intent': rasa_result.get('intent'),
                'confidence': rasa_result.get('confidence'),
                'entities': rasa_result.get('entities', []),
                'suggestions': openai_response.get('suggestions', [])
            }
        
        return rasa_response
    
    def enhance_rasa_response(self, response: str, entities: List[Dict]) -> str:
        """
        Enhance Rasa response với entity information
        """
        if not entities:
            return response
        
        # Add entity-specific information
        entity_info = []
        for entity in entities:
            entity_type = entity.get('entity')
            entity_value = entity.get('value')
            
            if entity_type == 'invoice_number':
                entity_info.append(f"Số hóa đơn: {entity_value}")
            elif entity_type == 'company_name':
                entity_info.append(f"Tên công ty: {entity_value}")
            elif entity_type == 'amount':
                entity_info.append(f"Số tiền: {entity_value}")
        
        if entity_info:
            response += f"\n\nThông tin đã nhận diện: {', '.join(entity_info)}"
        
        return response
    
    def get_intent_based_suggestions(self, intent: str) -> List[str]:
        """
        Generate suggestions based on intent
        """
        suggestions_map = {
            'ask_invoice_help': [
                'Tạo hóa đơn mới',
                'Tìm kiếm hóa đơn',
                'Hướng dẫn sử dụng',
                'Liên hệ hỗ trợ'
            ],
            'create_invoice_template': [
                'Xem template có sẵn',
                'Tạo template từ file',
                'Hướng dẫn thiết kế',
                'Test template'
            ],
            'extract_invoice_data': [
                'Upload file mới',
                'Kiểm tra kết quả OCR',
                'Sửa dữ liệu nhận diện',
                'Xuất dữ liệu Excel'
            ],
            'default': [
                'Hỏi về hóa đơn',
                'Tạo template',
                'Upload file',
                'Hỗ trợ kỹ thuật'
            ]
        }
        
        return suggestions_map.get(intent, suggestions_map['default'])
    
    def handle_invoice_extraction(self, entities: List[Dict]) -> Dict[str, Any]:
        """
        Custom logic cho invoice data extraction
        """
        return {
            'message': 'Tính năng trích xuất dữ liệu hóa đơn đang được phát triển. Vui lòng upload file để tôi hỗ trợ.',
            'type': 'text',
            'method': 'custom',
            'suggestions': [
                'Upload file hóa đơn',
                'Xem hướng dẫn OCR',
                'Kiểm tra format file',
                'Liên hệ hỗ trợ'
            ]
        }
    
    def handle_file_processing(self, entities: List[Dict]) -> Dict[str, Any]:
        """
        Custom logic cho file processing
        """
        return {
            'message': 'Vui lòng upload file hóa đơn để tôi có thể xử lý. Hỗ trợ: PDF, JPG, PNG, DOCX.',
            'type': 'text',
            'method': 'custom',
            'suggestions': [
                'Chọn file từ máy',
                'Chụp ảnh hóa đơn',
                'Kiểm tra format',
                'Xem kết quả mẫu'
            ]
        }
    
    def handle_template_matching(self, entities: List[Dict]) -> Dict[str, Any]:
        """
        Custom logic cho template matching
        """
        return {
            'message': 'Hệ thống template matching sẽ tự động nhận diện format hóa đơn và áp dụng template phù hợp.',
            'type': 'text',
            'method': 'custom',
            'suggestions': [
                'Xem danh sách template',
                'Tạo template mới',
                'Test template',
                'Tối ưu accuracy'
            ]
        }
    
    def combine_responses(self, rasa_response: Dict, openai_response: Dict) -> str:
        """
        Intelligent response combination
        """
        rasa_msg = rasa_response.get('message', '')
        openai_msg = openai_response.get('message', '')
        
        # If Rasa response is generic, use OpenAI
        if len(rasa_msg) < 50 or 'xin lỗi' in rasa_msg.lower():
            return openai_msg
        
        # If OpenAI is too long, prefer Rasa + summary
        if len(openai_msg) > 500:
            return f"{rasa_msg}\n\n💡 {openai_msg[:200]}..."
        
        # Combine both if complementary
        return f"{rasa_msg}\n\n📋 Chi tiết: {openai_msg}"
    
    def create_error_response(self, error: str) -> Dict[str, Any]:
        """
        Create error response
        """
        return {
            'message': 'Xin lỗi, tôi gặp sự cố kỹ thuật. Vui lòng thử lại sau.',
            'type': 'text',
            'method': 'error',
            'error': error,
            'suggestions': [
                'Thử lại',
                'Liên hệ hỗ trợ',
                'Báo cáo lỗi',
                'Sử dụng tính năng khác'
            ]
        }
    
    def create_fallback_response(self, message: str, rasa_result: Dict) -> Dict[str, Any]:
        """
        Fallback response when all methods fail
        """
        return {
            'message': f'Tôi hiểu bạn đang hỏi về "{message}". Tuy nhiên, tôi cần thêm thông tin để trả lời chính xác. Bạn có thể mô tả rõ hơn không?',
            'type': 'text',
            'method': 'fallback',
            'intent': rasa_result.get('intent', 'unknown'),
            'suggestions': [
                'Giải thích rõ hơn',
                'Hỏi câu khác',
                'Xem hướng dẫn',
                'Liên hệ hỗ trợ'
            ]
        }
    
    def get_conversation_context(self, user_id: str) -> List[Dict[str, str]]:
        """
        Get formatted conversation history for OpenAI
        """
        history = self.conversation_history.get(user_id, [])
        formatted = []
        
        for item in history[-6:]:  # Last 6 exchanges
            formatted.append({"role": "user", "content": item.get('user_message', '')})
            formatted.append({"role": "assistant", "content": item.get('bot_response', '')})
        
        return formatted
    
    def update_conversation_history(self, user_id: str, message: str, response: Dict, rasa_result: Dict):
        """
        Update conversation history
        """
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            'user_message': message,
            'bot_response': response.get('message', ''),
            'intent': rasa_result.get('intent'),
            'confidence': rasa_result.get('confidence'),
            'method': response.get('method'),
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 50 exchanges
        if len(self.conversation_history[user_id]) > 50:
            self.conversation_history[user_id] = self.conversation_history[user_id][-50:]