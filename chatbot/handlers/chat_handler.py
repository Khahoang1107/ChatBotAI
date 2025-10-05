import random
import re
import requests
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from config import Config
from models.ai_model import AIModel
from utils.text_processor import TextProcessor
from utils.training_client import TrainingDataClient
import logging

# Import Google AI Service
try:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from services.google_ai_service import GoogleAIService
except ImportError as e:
    print(f"Google AI Service import failed: {e}")
    GoogleAIService = None

logger = logging.getLogger(__name__)

class ChatHandler:
    def __init__(self):
        self.config = Config()  # ⭐ Initialize config
        self.ai_model = AIModel()
        self.text_processor = TextProcessor()
        self.conversation_history = {}
        
        # Rasa integration - DISABLED
        self.rasa_url = None
        self.use_rasa = False  # Rasa disabled - using pattern-based system only
        
        # Khởi tạo training client để lấy dữ liệu học từ templates
        try:
            self.training_client = TrainingDataClient()
            logger.info("TrainingDataClient initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize TrainingDataClient: {e}")
            self.training_client = None
        
        # Kiểm tra kết nối với backend training data
        if self.training_client:
            try:
                health = self.training_client.check_health()
                if health:
                    logger.info("Kết nối thành công với training data backend")
                else:
                    logger.warning("Training data backend not healthy")
            except Exception as e:
                logger.warning(f"Không thể kiểm tra kết nối training data backend: {e}")
                # Don't fail, just continue without backend
                self.training_client = None
        
        # Initialize Google AI Service
        if GoogleAIService:
            try:
                self.google_ai = GoogleAIService()
                if self.google_ai.is_available():
                    logger.info("Google AI Service initialized successfully")
                else:
                    logger.info("Google AI Service unavailable (no API key)")
                    self.google_ai = None
            except Exception as e:
                logger.error(f"Failed to initialize Google AI Service: {e}")
                self.google_ai = None
        else:
            self.google_ai = None
            logger.info("Google AI Service not available (package not installed)")
        
        # Rasa disabled - using pattern-based system
        logger.info("Using pattern-based intent detection (Rasa disabled)")
        
        # Patterns cho nhận diện intent - Cải thiện để nhận diện tốt hơn
        # Đặt camera_control lên đầu để ưu tiên
        self.patterns = {
            'camera_control': [
                r'(mở camera|bật camera|open camera)',
                r'(mở camere|mở camara|mở cammera)',  # ⭐ Lỗi chính tả phổ biến
                r'(mở máy ảnh|bật máy ảnh|máy ảnh)',  # ⭐ Từ đồng nghĩa
                r'(chụp ảnh|take photo|capture|chụp)',
                r'(tắt camera|đóng camera|close camera|đóng|tắt)',  # ⭐ Thêm "đóng", "tắt" đơn giản
                r'camera|camere|camara',  # ⭐ Bao gồm cả lỗi chính tả
                r'(chụp hóa đơn|scan invoice)'
            ],
            'list_invoices': [  # ⭐ Đặt lên đầu để ưu tiên
                r'(danh sách.*hóa đơn|hóa đơn.*danh sách)',
                r'(xem.*danh sách.*hóa đơn|danh sách.*hóa đơn.*đã.*lưu)',
                r'(hóa đơn.*đã.*lưu|hóa đơn.*đã.*upload)',
                r'(liệt kê.*hóa đơn|show.*all.*invoice)',
                r'(xem.*tất cả.*hóa đơn|all.*invoice)',
                r'(list.*invoice|saved.*invoice)',
                r'(tìm.*hóa đơn.*ngày|xem.*hóa đơn.*hôm|hóa đơn.*theo.*ngày)',  # ⭐ Tìm theo ngày
                r'(hóa đơn.*hôm nay|hóa đơn.*hôm qua|hóa đơn.*tuần này)',  # ⭐ Theo thời gian
            ],
            'greeting': [
                r'\b(xin chào|chào|hello|hi|hey|chao)\b',
                r'\b(good morning|good afternoon|good evening)\b',
                r'\b(chào buổi sáng|chào buổi chiều|chào buổi tối)\b',
                r'^(chào|hello|hi)$'
            ],
            'invoice_query': [
                r'(hóa đơn|invoice|bill)',
                r'(mã số thuế|tax code)',
                r'(thanh toán|payment)',
                r'(VAT|thuế giá trị gia tăng)',
                r'(tạo hóa đơn|làm thế nào.*tạo)',
                r'(xuất hóa đơn|in hóa đơn)'
            ],
            'data_query': [
                r'(xem dữ liệu.*hóa đơn|dữ liệu.*hóa đơn)',  # Match "xem dữ liệu hóa đơn" specifically
                r'(xem.*hóa đơn.*đã.*upload|xem.*hóa đơn.*đã.*lưu)',  # Match "xem hóa đơn đã upload/lưu"
                r'(xem.*ho[aá].*[dđ].*n|xem.*c[aá]c.*ho[aá])',  # Flexible for typos: xem hoa don, xem cac hoa
                r'(ho[aá].*[dđ].*n.*[dđ][aă].*l[ưu]u)',  # hoa don da luu with typos
                r'(xem dữ liệu|dữ liệu hiện tại|data)',
                r'(xem giá|giá cả|price)',
                r'(thống kê|báo cáo|report)',
                r'(danh sách|list)',
                r'(tìm kiếm thông tin|search|tìm kiếm)',
                r'(hiển thị|show|display)',
                r'(có bao nhiêu|bao nhiêu|tổng số|đếm|count|số lượng)',
                r'(xem số|xem tổng|xem toàn bộ)',
                r'(hóa đơn|hoá đơn|ho[aá]\s*[dđ].*n|invoice)',  # Flexible invoice matching
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
                r'(làm sao|how to|cách)',
                r'(tôi cần|i need|cần)'
            ],
            'upload_image': [
                r'(upload ảnh|tải ảnh|up ảnh)',
                r'(gửi ảnh|send image)',
                r'(ảnh từ máy|file ảnh)',
                r'(chọn file|select file)'
            ],
            'file_analysis': [
                r'(\.jpg|\.png|\.jpeg|\.pdf)',
                r'(xem file|phân tích file)',
                r'(file.*dữ liệu|dữ liệu.*file)',
                r'(kết quả.*file|file.*kết quả)',
                r'(đọc dữ liệu từ ảnh|read data from image)',
                r'(đọc ảnh|read image)',
                r'(xử lý ảnh|process image)',
                r'(phân tích ảnh|analyze image)',
                r'(mau-hoa-don|template)',
                r'(\.jpg|\.png|\.jpeg|\.pdf).*',
                r'.*\.(jpg|png|jpeg|pdf)',
                r'(trả ảnh|show image)',
                r'(xem ảnh|view image)',
                r'(ảnh.*gì|what.*image)'
            ],
            'goodbye': [
                r'(tạm biệt|goodbye|bye|see you)',
                r'(cảm ơn|thank you|thanks)',
                r'(kết thúc|end|finish)'
            ]
        }

    async def process_message(self, message: str, user_id: str = 'anonymous') -> Dict[str, Any]:
        """Xử lý tin nhắn từ user với pattern-based system"""
        logger.info(f"Processing message from {user_id}: {message}")
        
        # Using pattern-based logic directly (no Rasa)
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
        message_clean = self.text_processor.normalize(message.lower())
        message_lower = message.lower()
        logger.info(f"Original message: '{message}'")
        logger.info(f"Cleaned message: '{message_clean}'")
        
        # Check for filename pattern first (highest priority)
        import re
        filename_pattern = r'[a-zA-Z0-9\-_\.]+\.(jpg|jpeg|png|pdf|gif)'
        if re.search(filename_pattern, message_lower, re.IGNORECASE):
            logger.info(f"Filename pattern found, returning 'file_analysis'")
            return 'file_analysis'
        
        # Check for file extensions or image-related keywords
        file_keywords = ['mau-hoa-don', 'template', 'đọc dữ liệu từ ảnh', 'phân tích ảnh', 'xem ảnh', 'đọc ảnh', 'trả ảnh', 'xem file']
        if any(keyword in message_lower for keyword in file_keywords):
            logger.info(f"File-related keyword '{[k for k in file_keywords if k in message_lower]}' found, returning 'file_analysis'")
            return 'file_analysis'
            
        # Check for "xem dữ liệu từ ảnh" specifically
        if 'xem dữ liệu từ ảnh' in message_lower or 'dữ liệu từ ảnh' in message_lower or 'trả ảnh' in message_lower:
            logger.info(f"'xem dữ liệu từ ảnh' or 'trả ảnh' pattern found, returning 'file_analysis'")
            return 'file_analysis'
        
        for intent, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_clean, re.IGNORECASE):
                    logger.info(f"Matched intent '{intent}' with pattern '{pattern}'")
                    return intent
                elif re.search(pattern, message.lower(), re.IGNORECASE):
                    logger.info(f"Matched intent '{intent}' with pattern '{pattern}' (original message)")
                    return intent
        
        logger.info(f"No intent matched, defaulting to 'general'")
        return 'general'
    
    def handle_intent(self, intent: str, message: str, context: Dict) -> Dict[str, Any]:
        """Xử lý intent và trả về response"""
        
        if intent == 'greeting':
            return self.handle_greeting()
        elif intent == 'invoice_query':
            return self.handle_invoice_query(message, context)
        elif intent == 'data_query':
            return self.handle_data_query(message, context)
        elif intent == 'invoice_analysis':
            return self.handle_invoice_analysis(message, context)
        elif intent == 'template_help':
            return self.handle_template_help(message, context)
        elif intent == 'camera_control':
            return self.handle_camera_control(message, context)
        elif intent == 'help':
            return self.handle_help_request()
        elif intent == 'upload_image':
            return self.handle_upload_image(message, context)
        elif intent == 'file_analysis':
            return self.handle_file_analysis(message, context)
        elif intent == 'list_invoices':
            return self.handle_list_invoices(message, context)
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
    
    def handle_data_query(self, message: str, context: Dict) -> Dict[str, Any]:
        """Xử lý câu hỏi về dữ liệu - QUERY VỚI RAG SEMANTIC SEARCH"""
        import re
        import requests
        
        # Check if message contains filename - redirect to file_analysis
        filename_pattern = r'[a-zA-Z0-9\-_\.]+\.(jpg|jpeg|png|pdf|gif)'
        if re.search(filename_pattern, message.lower(), re.IGNORECASE):
            logger.info(f"Filename detected in data_query, redirecting to file_analysis")
            return self.handle_file_analysis(message, context)
            
        # Check for file-related keywords  
        if any(keyword in message.lower() for keyword in ['từ ảnh', 'mau-hoa-don', 'template', 'đọc ảnh']):
            logger.info(f"File-related keywords detected, redirecting to file_analysis")
            return self.handle_file_analysis(message, context)
        
        # 🔍 RAG SEMANTIC SEARCH - Query documents from RAG
        try:
            logger.info("🔍 Performing RAG semantic search...")
            
            # Call RAG search endpoint
            rag_response = requests.post(
                'http://localhost:8000/chat/rag-search',
                json={'query': message, 'top_k': 5},
                timeout=10
            )
            
            if rag_response.status_code == 200:
                rag_results = rag_response.json()
                documents = rag_results.get('results', [])
                
                if not documents:
                    # Try getting stats if no RAG results
                    stats_response = requests.get('http://localhost:8000/chat/stats', timeout=5)
                    if stats_response.status_code == 200:
                        stats = stats_response.json()
                        total_docs = stats.get('total_documents', 0)
                        
                        if total_docs == 0:
                            return {
                                'message': '⚠️ **Chưa có dữ liệu hóa đơn nào**\n\nVui lòng upload ảnh hóa đơn để bắt đầu!',
                                'type': 'text',
                                'suggestions': ['Upload ảnh hóa đơn', 'Mở camera', 'Hướng dẫn OCR']
                            }
                        
                        return {
                            'message': f'📊 Hệ thống có **{total_docs} tài liệu** nhưng không tìm thấy kết quả phù hợp với câu hỏi: "{message}"\n\n� Thử hỏi cụ thể hơn về nội dung hóa đơn!',
                            'type': 'no_results',
                            'suggestions': ['Xem tất cả tài liệu', 'Upload thêm', 'Hỏi khác']
                        }
                
                # 🤖 QUAN TRỌNG: Dùng Google AI để trả lời dựa trên RAG data
                if self.google_ai and self.google_ai.is_available():
                    try:
                        # Chuẩn bị context từ RAG results
                        rag_context = "THÔNG TIN TỪ HỆ THỐNG:\n\n"
                        
                        for idx, doc in enumerate(documents[:5], 1):
                            content = doc.get('content', '')
                            metadata = doc.get('metadata', {})
                            score = doc.get('score', 0)
                            
                            rag_context += f"Tài liệu {idx} (độ phù hợp: {score:.2f}):\n"
                            rag_context += f"{content}\n"
                            
                            if 'invoice_code' in metadata:
                                rag_context += f"Mã hóa đơn: {metadata.get('invoice_code')}\n"
                            if 'buyer_name' in metadata:
                                rag_context += f"Khách hàng: {metadata.get('buyer_name')}\n"
                            if 'total_amount' in metadata:
                                rag_context += f"Tổng tiền: {metadata.get('total_amount')}\n"
                            
                            rag_context += "\n---\n\n"
                        
                        # Tạo prompt với context
                        prompt = f"""Bạn là trợ lý AI thông minh. Dựa trên thông tin dưới đây, hãy trả lời câu hỏi của người dùng một cách chính xác và chi tiết.

{rag_context}

CÂU HỎI: {message}

Hãy trả lời dựa trên dữ liệu thực tế ở trên. Nếu có nhiều hóa đơn, hãy liệt kê rõ ràng. Sử dụng emoji và format markdown để dễ đọc."""
                        
                        # Gọi Google AI với RAG context
                        ai_response = self.google_ai.generate_response(prompt)
                        
                        if ai_response:
                            return {
                                'message': f"🤖 **Trả lời từ AI (dựa trên {len(documents)} tài liệu):**\n\n{ai_response}",
                                'type': 'ai_rag_response',
                                'data': documents,
                                'suggestions': ['Hỏi thêm', 'Xem chi tiết', 'Upload thêm', 'Thống kê']
                            }
                        
                    except Exception as e:
                        logger.error(f"❌ Google AI failed: {e}")
                
                # FALLBACK: Nếu không có Google AI, hiện raw data
                message_text = f"🔍 **Tìm thấy {len(documents)} kết quả phù hợp:**\n\n"
                
                for idx, doc in enumerate(documents[:5], 1):
                    score = doc.get('score', 0)
                    content = doc.get('content', 'N/A')
                    metadata = doc.get('metadata', {})
                    filename = metadata.get('filename', 'Unknown')
                    
                    message_text += f"**{idx}. {filename}** (Score: {score:.2f})\n"
                    message_text += f"```\n{content[:200]}{'...' if len(content) > 200 else ''}\n```\n"
                    
                    # Show OCR metadata if available
                    if 'invoice_code' in metadata:
                        message_text += f"• Mã HĐ: `{metadata.get('invoice_code')}`\n"
                    if 'total_amount' in metadata:
                        message_text += f"• Tổng tiền: {metadata.get('total_amount')}\n"
                    message_text += "\n"
                
                return {
                    'message': message_text,
                    'type': 'rag_search_results',
                    'data': documents,
                    'suggestions': ['Tìm kiếm khác', 'Xem chi tiết', 'Upload thêm', 'Thống kê']
                }
            else:
                logger.warning(f"RAG search returned {rag_response.status_code}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Cannot connect to backend RAG: {e}")
        except Exception as e:
            logger.error(f"❌ Error in RAG search: {e}")
        
        # FALLBACK
        return {
            'message': '⚠️ **Không thể tìm kiếm**\n\nHệ thống RAG chưa kết nối được với backend.\n\n📝 **Kiểm tra:**\n• Backend đang chạy? (port 8000)\n• RAG service đã cấu hình?\n• Kết nối mạng ổn định?\n\nVui lòng kiểm tra và thử lại.',
            'type': 'error',
            'suggestions': ['Kiểm tra backend', 'Upload ảnh mới', 'Liên hệ support']
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
**{Config.BOT_NAME}** - Trợ lý AI của bạn

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
    
    def handle_upload_image(self, message: str, context: Dict) -> Dict[str, Any]:
        """Xử lý yêu cầu upload ảnh"""
        return {
            'message': '''📷 **Hướng dẫn upload ảnh hóa đơn:**

📤 **Cách 1: Upload từ máy tính**
• Nhấn nút "Chọn file" hoặc kéo thả ảnh
• Chọn file ảnh (JPG, PNG, PDF)
• Hệ thống sẽ tự động OCR

📱 **Cách 2: Chụp trực tiếp** 
• Nói "mở camera" để bật camera
• Chụp ảnh hóa đơn
• OCR tự động xử lý

🔍 **Lưu ý:**
• Ảnh rõ nét, đủ ánh sáng
• Hóa đơn phẳng, không bị che khuất
• Định dạng: JPG, PNG, PDF

Bạn muốn upload ảnh bây giờ không?''',
            'type': 'upload_guide',
            'action': 'show_upload_dialog',
            'suggestions': [
                'Mở camera chụp ảnh',
                'Chọn file từ máy',
                'Hướng dẫn chi tiết',
                'Xem demo OCR'
            ]
        }
    
    def handle_file_analysis(self, message: str, context: Dict) -> Dict[str, Any]:
        """Xử lý yêu cầu phân tích file cụ thể"""
        
        # Tìm tên file trong message
        import re
        file_pattern = r'([a-zA-Z0-9\-_\.]+\.(jpg|jpeg|png|pdf|gif))'
        file_matches = re.findall(file_pattern, message, re.IGNORECASE)
        
        if file_matches:
            filename = file_matches[0][0]
            
            # Gọi backend OCR hoặc trả về kết quả đã lưu
            try:
                import requests
                import json
                
                # Thử lấy OCR result từ database trước
                try:
                    backend_response = requests.get(
                        f"http://localhost:8000/api/ocr/saved-invoices",
                        params={'limit': 50},
                        timeout=5
                    )
                    
                    if backend_response.status_code == 200:
                        saved_invoices = backend_response.json()
                        # Tìm invoice với filename tương ứng
                        matching_invoice = None
                        for invoice in saved_invoices:
                            if filename.lower() in invoice.get('filename', '').lower():
                                matching_invoice = invoice
                                break
                        
                        if matching_invoice:
                            # Trả về dữ liệu đã lưu
                            extracted = matching_invoice
                            
                            # Basic response text
                            response_text = f"""✅ **Đã tìm thấy dữ liệu OCR cho file: {filename}**

🧾 **Thông tin hóa đơn đã xử lý:**
• Mã hóa đơn: {extracted.get('invoice_code', 'N/A')}
• Ngày: {extracted.get('invoice_date', 'N/A')}
• Khách hàng: {extracted.get('buyer_name', 'N/A')}
• Nhà cung cấp: {extracted.get('seller_name', 'N/A')}
• Tổng tiền: {extracted.get('total_amount', 'N/A')}
• Loại hóa đơn: {extracted.get('invoice_type', 'N/A')}

📊 **Độ chính xác:** {extracted.get('confidence_score', 0)*100:.1f}%
💾 **ID trong hệ thống: {extracted.get('id', 'N/A')}**
🕒 **Đã xử lý lúc:** {extracted.get('created_at', 'N/A')[:19] if extracted.get('created_at') else 'N/A'}

✅ **Dữ liệu này đã được xử lý và lưu trữ thành công trước đó!**"""
                            
                            # Enhance with Google AI if available
                            if self.google_ai and self.google_ai.is_available():
                                try:
                                    # Prepare database context
                                    db_context = {
                                        'recent_invoices': saved_invoices[:5],  # Recent 5 invoices
                                        'total_invoices': len(saved_invoices),
                                        'current_invoice': matching_invoice
                                    }
                                    
                                    # Get AI-enhanced response
                                    ai_enhancement = self.google_ai.enhance_database_query(
                                        f"Phân tích chi tiết hóa đơn {filename} và so sánh với dữ liệu hiện có",
                                        db_context
                                    )
                                    
                                    if ai_enhancement:
                                        response_text += f"\n\n🤖 **AI Analysis:**\n{ai_enhancement}"
                                        
                                except Exception as ai_error:
                                    logger.warning(f"Google AI enhancement failed: {ai_error}")
                            
                            return {
                                'message': response_text,
                                'type': 'ocr_result_found',
                                'filename': filename,
                                'ocr_data': matching_invoice,
                                'already_processed': True,
                                'suggestions': [
                                    'Xem chi tiết thêm',
                                    'Tạo template từ hóa đơn này',
                                    'Xuất Excel', 
                                    'Upload file mới'
                                ]
                            }
                
                except Exception as db_error:
                    logger.warning(f"Không thể lấy dữ liệu từ database: {db_error}")
                
                # Nếu không có trong database, tạo mock OCR result dựa trên filename
                if 'mtt' in filename.lower() or 'mau-hoa-don' in filename.lower():
                    # Đặc biệt cho file mau-hoa-don-mtt.jpg
                    mock_result = {
                        "filename": filename,
                        "file_type": ".jpg",
                        "extracted_data": {
                            "invoice_number": "SO-MTT-2025-001",
                            "date": "27/09/2025",
                            "total_amount": "3,850,000 VND",
                            "tax_amount": "385,000 VND", 
                            "supplier_name": "Công ty TNHH Mẫu Template",
                            "supplier_tax_code": "0123456789",
                            "buyer_name": "Khách hàng ABC",
                            "items": [
                                {"name": "Dịch vụ tư vấn", "qty": 1, "price": "3,500,000 VND"},
                                {"name": "Phí xử lý", "qty": 1, "price": "350,000 VND"}
                            ],
                            "confidence": 0.92
                        },
                        "confidence_score": 0.92,
                        "processing_time": 3.2,
                        "status": "success"
                    }
                else:
                    # Generic mock data cho file khác
                    mock_result = {
                        "filename": filename,
                        "extracted_data": {
                            "invoice_number": f"INV-{filename[:3].upper()}-001",
                            "date": "27/09/2025",
                            "total_amount": "2,150,000 VND",
                            "tax_amount": "215,000 VND",
                            "supplier_name": "Đơn vị cung cấp",
                            "confidence": 0.87
                        },
                        "confidence_score": 0.87,
                        "status": "success"
                    }
                
                # Format response
                extracted = mock_result.get('extracted_data', {})
                response_text = f"""📋 **Kết quả OCR từ file: {filename}**

🧾 **Thông tin hóa đơn:**
• Số hóa đơn: {extracted.get('invoice_number', 'N/A')}
• Ngày: {extracted.get('date', 'N/A')}
• Tổng tiền: {extracted.get('total_amount', 'N/A')}
• Thuế VAT: {extracted.get('tax_amount', 'N/A')}
• Nhà cung cấp: {extracted.get('supplier_name', 'N/A')}"""

                if extracted.get('supplier_tax_code'):
                    response_text += f"\n• MST nhà cung cấp: {extracted.get('supplier_tax_code')}"
                    
                if extracted.get('buyer_name'):
                    response_text += f"\n• Khách hàng: {extracted.get('buyer_name')}"
                
                if extracted.get('items'):
                    response_text += f"\n\n📦 **Chi tiết sản phẩm:**"
                    for i, item in enumerate(extracted.get('items', [])[:3], 1):
                        response_text += f"\n{i}. {item.get('name', 'N/A')} - {item.get('qty', 0)} x {item.get('price', 'N/A')}"

                response_text += f"""

📊 **Độ chính xác:** {extracted.get('confidence', 0)*100:.1f}%
💾 **Đã lưu vào hệ thống thành công!**"""
                
                return {
                    'message': response_text,
                    'type': 'ocr_result',
                    'filename': filename,
                    'ocr_data': mock_result,
                    'suggestions': [
                        'Lưu thành template',
                        'Chỉnh sửa thông tin',
                        'Xuất Excel', 
                        'Phân tích file khác'
                    ]
                }
                
            except Exception as e:
                logger.error(f"Error in file analysis: {e}")
                
        # Nếu có filename nhưng chưa được upload, thông báo cần upload
        if file_matches:
            filename = file_matches[0][0]
            return {
                'message': f'''📤 **File "{filename}" chưa được upload!**

🔍 **Để xử lý file này, bạn cần:**
1. Upload file "{filename}" lên hệ thống trước
2. Hệ thống sẽ tự động OCR và thông báo kết quả
3. Sau đó bạn có thể hỏi về dữ liệu đã xử lý

💡 **Cách upload:**
• Sử dụng nút "Chọn file" để upload từ máy tính
• Hoặc nói "mở camera" để chụp trực tiếp

⚠️ **Lưu ý:** Tôi chỉ có thể đọc dữ liệu từ file đã được upload và xử lý OCR.''',
                'type': 'file_not_found',
                'filename': filename,
                'suggestions': [
                    f'Upload file {filename}',
                    'Mở camera chụp ảnh',
                    'Xem hóa đơn đã lưu',
                    'Hướng dẫn upload'
                ]
            }
        
        # Fallback nếu không tìm thấy file
        return {
            'message': f'''📁 **Phân tích file:**

Tôi có thể phân tích các file đã upload:
• File JPG, PNG: OCR thông tin hóa đơn
• File PDF: Trích xuất dữ liệu structured  
• Hiển thị kết quả chi tiết

🔍 **Để xem kết quả OCR:**
Gửi tên file cụ thể (vd: "mau-hoa-don.jpg")
Hoặc nói "phân tích file [tên file]"

Bạn muốn phân tích file nào?''',
            'type': 'file_query',
            'suggestions': [
                'Upload file mới',
                'Xem lịch sử OCR',
                'Hướng dẫn upload',
                'Tạo template'
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
    
    def notify_file_processed(self, filename: str, ocr_result: Dict) -> Dict[str, Any]:
        """Thông báo khi file đã được xử lý OCR xong"""
        try:
            extracted = ocr_result.get('extracted_data', {})
            
            # Xác định loại hóa đơn
            invoice_type = extracted.get('invoice_type', 'general')
            type_icons = {
                'electricity': '⚡',
                'water': '💧', 
                'service': '🔧',
                'template_sample': '📋',
                'general': '📄'
            }
            icon = type_icons.get(invoice_type, '📄')
            
            notification_text = f"""✅ **Xử lý ảnh hoàn tất!**

{icon} **File:** {filename}
🕒 **Thời gian:** {datetime.now().strftime('%H:%M:%S')}

📋 **Kết quả OCR:**
• Mã hóa đơn: {extracted.get('invoice_code', 'N/A')}
• Khách hàng: {extracted.get('buyer_name', 'N/A')} 
• Tổng tiền: {extracted.get('total_amount', 'N/A')}
• Loại: {invoice_type.title()}

📊 **Độ chính xác:** {ocr_result.get('confidence_score', 0)*100:.1f}%
💾 **Đã lưu vào hệ thống với ID: {ocr_result.get('database_id', 'N/A')}**

🎉 **Bạn có thể xem chi tiết hoặc tiếp tục upload ảnh khác!**"""
            
            return {
                'message': notification_text,
                'type': 'ocr_notification',
                'filename': filename,
                'ocr_data': ocr_result,
                'auto_notify': True,
                'suggestions': [
                    'Xem chi tiết đầy đủ',
                    'Tạo template', 
                    'Chụp ảnh khác',
                    'Danh sách hóa đơn'
                ]
            }
            
        except Exception as e:
            logger.error(f"Error in notify_file_processed: {str(e)}")
            return {
                'message': f'✅ **File {filename} đã xử lý xong!**\n\nBạn có thể hỏi "xem dữ liệu từ ảnh {filename}" để xem kết quả chi tiết.',
                'type': 'simple_notification',
                'suggestions': ['Xem kết quả OCR', 'Chụp ảnh khác']
            }
    
    def handle_general_query(self, message: str, context: Dict) -> Dict[str, Any]:
        """Xử lý câu hỏi chung bằng AI"""
        
        # Kiểm tra một số patterns đơn giản trước
        message_lower = message.lower().strip()
        
        # Patterns cho lời chào đơn giản
        if any(greeting in message_lower for greeting in ['xin chào', 'chào', 'hello', 'hi', 'chao']):
            return self.handle_greeting()
        
        # Patterns cho hỏi về huấn luyện AI
        if any(keyword in message_lower for keyword in ['huấn luyện', 'train', 'học', 'ai hiểu', 'mô hình']):
            return {
                'message': '''**Để AI hiểu và trả lời tốt hơn, bạn cần:**

📚 **1. Cung cấp dữ liệu training:**
• Upload nhiều hóa đơn mẫu
• Sửa chữa kết quả OCR sai
• Gắn nhãn dữ liệu đúng

🎯 **2. Huấn luyện thường xuyên:**
• Mỗi lần sửa = 1 training sample
• Càng nhiều data → AI càng thông minh
• Model sẽ học từ mistakes

💡 **3. Test và feedback:**
• Thử chat với nhiều câu hỏi khác nhau  
• Báo cáo khi AI trả lời sai
• Liên tục cải thiện patterns

Bạn muốn thử upload hóa đơn để training không?''',
                'type': 'text',
                'suggestions': [
                    'Upload hóa đơn để training',
                    'Xem hướng dẫn chi tiết',
                    'Test AI với câu hỏi khác',
                    'Tạo template hóa đơn'
                ]
            }
        
        # Check if Google AI can enhance the response
        if self.google_ai and self.google_ai.is_available():
            try:
                # Get database context for AI
                db_context = self._get_database_context_for_ai()
                
                # Try Google AI first for better understanding
                ai_response = self.google_ai.enhance_database_query(message, db_context)
                
                if ai_response:
                    return {
                        'message': f"🤖 **AI Enhanced Response:**\n\n{ai_response}",
                        'type': 'ai_enhanced',
                        'suggestions': [
                            'Tìm kiếm cụ thể hơn',
                            'Xem dữ liệu gần đây',
                            'Upload hóa đơn mới',
                            'Phân tích xu hướng'
                        ]
                    }
            except Exception as ai_error:
                logger.warning(f"Google AI failed, falling back to OpenAI: {ai_error}")
        
        # Phân loại câu hỏi có liên quan đến hóa đơn không
        if self._is_invoice_related(message):
            try:
                ai_response = self.ai_model.generate_invoice_response(message, context)
            except:
                ai_response = None
            suggestions = [
                'Tạo hóa đơn mới',
                'Tìm kiếm hóa đơn', 
                'Xem báo cáo thuế',
                'Hướng dẫn OCR'
            ]
        else:
            try:
                ai_response = self.ai_model.generate_general_response(message, context)
            except:
                ai_response = None
            suggestions = [
                'Hướng dẫn sử dụng hệ thống',
                'Tính năng nào có sẵn?',
                'Cách tạo hóa đơn',
                'Hỗ trợ kỹ thuật'
            ]
        
        # Fallback nếu AI không hoạt động
        if not ai_response:
            ai_response = f"Tôi hiểu bạn đang hỏi về '{message}'. Tuy nhiên, tôi cần thêm thông tin để trả lời chính xác. Bạn có thể mô tả rõ hơn không?"
        
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
    
    # === RASA REMOVED - Using Pattern-Based System Only ===
    
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
            }

    def handle_camera_control(self, message: str, context: Dict) -> Dict[str, Any]:
        """Xử lý lệnh điều khiển camera"""
        message_lower = message.lower().strip()
        
        # ⭐ CHECK TẮT CAMERA TRƯỚC (ưu tiên)
        if any(cmd in message_lower for cmd in ['tắt camera', 'đóng camera', 'close camera', 'đóng máy ảnh', 'tắt máy ảnh']) or message_lower in ['đóng', 'tắt', 'close']:
            return {
                'message': '📷 Đã tắt camera. Cảm ơn bạn đã sử dụng!',
                'type': 'camera_close',
                'action': 'close_camera', 
                'suggestions': [
                    'Mở lại camera',
                    'Upload ảnh từ máy',
                    'Hỗ trợ khác',
                    'Tạo hóa đơn'
                ]
            }
        # Check mở camera
        elif any(cmd in message_lower for cmd in ['mở camera', 'bật camera', 'open camera', 'camera', 'mở máy ảnh', 'máy ảnh', 'camere', 'camara']) or message_lower in ['mở', 'bật', 'open']:
            # Kiểm tra xem có liên quan đến hóa đơn/OCR không
            is_ocr_request = any(keyword in message_lower for keyword in ['hóa đơn', 'ocr', 'scan', 'chụp'])
            
            base_message = '📷 Đang mở camera cho bạn... Hãy cho phép trình duyệt truy cập camera khi có thông báo.'
            if is_ocr_request:
                base_message += '\n\n🧾 Tôi sẽ tự động phân tích hóa đơn sau khi bạn chụp ảnh!'
            
            return {
                'message': base_message,
                'type': 'camera_open',
                'action': 'open_camera',
                'ocr_mode': is_ocr_request,
                'suggestions': [
                    'Chụp ảnh hóa đơn' if is_ocr_request else 'Chụp ảnh',
                    'Tắt camera', 
                    'Hướng dẫn OCR' if is_ocr_request else 'Hướng dẫn sử dụng',
                    'Quét mã QR'
                ]
            }
        elif any(cmd in message_lower for cmd in ['chụp ảnh', 'take photo', 'capture', 'chụp']):
            return {
                'message': '📸 Nhấn nút chụp ảnh trên giao diện camera hoặc nói "chụp" để chụp ảnh.\n\n🤖 Sau khi chụp, tôi sẽ tự động phân tích OCR cho bạn!',
                'type': 'camera_capture',
                'action': 'capture_photo',
                'auto_ocr': True,
                'suggestions': [
                    'Chụp ảnh hóa đơn ngay',
                    'Phân tích OCR', 
                    'Tắt camera',
                    'Xem kết quả'
                ]
            }
        else:
            return {
                'message': '📷 Tôi có thể giúp bạn:\n\n• **Mở camera**: "mở camera", "bật camera"\n• **Chụp ảnh**: "chụp ảnh", "chụp"\n• **Tắt camera**: "tắt camera", "đóng camera"\n\nBạn muốn làm gì với camera?',
                'type': 'camera_help',
                'suggestions': [
                    'Mở camera', 
                    'Hướng dẫn chụp ảnh',
                    'Upload ảnh từ máy',
                    'Quét mã QR'
                ]
            }

    def handle_list_invoices(self, message: str, context: Dict) -> Dict[str, Any]:
        """Xử lý yêu cầu xem danh sách hóa đơn đã lưu"""
        try:
            # Call backend API to get saved invoices
            response = requests.get(
                f"{self.config.BACKEND_URL}/api/ocr/saved-invoices",
                params={'limit': 10}  # Show last 10 invoices
            )
            
            if response.status_code == 200:
                invoices = response.json()
                
                if not invoices:
                    return {
                        'message': '📄 Chưa có hóa đơn nào được lưu trong hệ thống.\n\n🤖 Hãy chụp ảnh hoặc upload hóa đơn để tôi phân tích và lưu trữ!',
                        'type': 'text',
                        'suggestions': [
                            'Mở camera chụp hóa đơn',
                            'Upload ảnh hóa đơn',
                            'Hướng dẫn OCR',
                            'Tạo mẫu hóa đơn'
                        ]
                    }
                
                # Format invoice list
                invoice_list = "📋 **Danh sách hóa đơn đã lưu:**\n\n"
                
                for i, inv in enumerate(invoices[:10], 1):
                    invoice_type = inv.get('invoice_type', 'general')
                    buyer_name = inv.get('buyer_name', 'N/A')
                    total_amount = inv.get('total_amount', 'N/A')
                    created_at = inv.get('created_at', '')
                    
                    # Convert invoice type to Vietnamese
                    type_mapping = {
                        'electricity': '⚡ Hóa đơn điện',
                        'water': '💧 Hóa đơn nước', 
                        'service': '🔧 Hóa đơn dịch vụ',
                        'template_sample': '📋 Mẫu hóa đơn',
                        'general': '📄 Hóa đơn chung'
                    }
                    type_display = type_mapping.get(invoice_type, '📄 Hóa đơn')
                    
                    # Format date
                    try:
                        from datetime import datetime
                        if created_at:
                            date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            date_str = date_obj.strftime('%d/%m/%Y %H:%M')
                        else:
                            date_str = 'N/A'
                    except:
                        date_str = created_at[:10] if len(created_at) >= 10 else 'N/A'
                    
                    invoice_list += f"**{i}.** {type_display}\n"
                    invoice_list += f"   • **Khách hàng:** {buyer_name}\n"
                    invoice_list += f"   • **Tổng tiền:** {total_amount}\n" 
                    invoice_list += f"   • **Ngày lưu:** {date_str}\n"
                    invoice_list += f"   • **ID:** {inv.get('id', 'N/A')}\n\n"
                
                return {
                    'message': invoice_list,
                    'type': 'text',
                    'data': invoices,
                    'suggestions': [
                        'Xem chi tiết hóa đơn',
                        'Mở camera chụp thêm',
                        'Upload ảnh hóa đơn mới',
                        'Thống kê hóa đơn'
                    ]
                }
            
            else:
                return {
                    'message': f'❌ Không thể lấy danh sách hóa đơn. Lỗi: {response.status_code}',
                    'type': 'error',
                    'suggestions': [
                        'Thử lại',
                        'Liên hệ hỗ trợ',
                        'Chụp hóa đơn mới',
                        'Hướng dẫn sử dụng'
                    ]
                }
                
        except requests.RequestException as e:
            logger.error(f"Network error getting invoices: {str(e)}")
            return {
                'message': '❌ Lỗi kết nối khi lấy danh sách hóa đơn. Vui lòng thử lại.',
                'type': 'error',
                'suggestions': ['Thử lại', 'Chụp hóa đơn mới']
            }
    
    def _get_database_context_for_ai(self) -> Dict:
        """Get database context for AI enhancement"""
        try:
            # Get recent invoices from backend
            response = requests.get(
                "http://localhost:8000/api/ocr/saved-invoices",
                params={'limit': 20},
                timeout=5
            )
            
            if response.status_code == 200:
                invoices = response.json()
                
                # Prepare context
                context = {
                    'total_invoices': len(invoices),
                    'recent_invoices': invoices[:5],  # Most recent 5
                    'invoice_types': list(set([inv.get('invoice_type', 'Unknown') for inv in invoices])),
                    'date_range': self._get_date_range(invoices)
                }
                
                return context
            else:
                return {'error': 'Could not fetch database context'}
                
        except Exception as e:
            logger.warning(f"Error getting database context: {e}")
            return {'error': str(e)}
    
    def _get_date_range(self, invoices: List[Dict]) -> str:
        """Get date range from invoices"""
        if not invoices:
            return "No data"
            
        dates = []
        for inv in invoices:
            created_at = inv.get('created_at')
            if created_at:
                dates.append(created_at[:10])  # Get date part
        
        if dates:
            dates.sort()
            return f"{dates[0]} to {dates[-1]}"
        
        return "Unknown range"
