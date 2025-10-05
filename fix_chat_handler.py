"""Script to fix chat_handler.py - replace handle_data_query with Azure API version"""
import re

file_path = r'f:\DoAnCN\chatbot\handlers\chat_handler.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the function start and end
pattern = r'(    def handle_data_query\(self, message: str, context: Dict\) -> Dict\[str, Any\]:.*?)(\n    def handle_invoice_analysis)'

new_function = r'''    def handle_data_query(self, message: str, context: Dict) -> Dict[str, Any]:
        """Xử lý câu hỏi về dữ liệu - QUERY TỪ AZURE STORAGE VIA BACKEND API"""
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
        
        # ☁️ QUERY AZURE STORAGE VIA BACKEND API
        try:
            logger.info("☁️ Querying Azure Storage via Backend API...")
            
            response = requests.get('http://localhost:8000/chat/stats', timeout=5)
            
            if response.status_code == 200:
                stats = response.json()
                total_docs = stats.get('total_documents', 0)
                
                if total_docs == 0:
                    return {
                        'message': '⚠️ **Chưa có dữ liệu hóa đơn nào**\n\nVui lòng upload ảnh hóa đơn để bắt đầu!',
                        'type': 'text',
                        'suggestions': ['Upload ảnh hóa đơn', 'Mở camera', 'Hướng dẫn OCR']
                    }
                
                message_text = f"""📊 **Thống kê hệ thống:**

📁 **Tổng quan:**
• Tổng số tài liệu: **{total_docs}**
• Phiên chat: **{stats.get('total_sessions', 0)}**
• Tin nhắn: **{stats.get('total_messages', 0)}**
• Truy vấn: **{stats.get('total_queries', 0)}**
• Kết nối active: **{stats.get('active_connections', 0)}**

☁️ **Azure Storage & RAG:**
• Documents: {stats.get('rag_stats', {}).get('total_documents', 0)}
• Vectors: {stats.get('rag_stats', {}).get('total_vectors', 0)}

💡 **Bạn có thể:**
• Upload thêm hóa đơn
• Hỏi về nội dung hóa đơn đã upload
• Tìm kiếm thông tin cụ thể"""
                
                # Add Google AI enhancement
                if self.google_ai and self.google_ai.is_available():
                    try:
                        ai_insight = self.google_ai.enhance_database_query(
                            f"Phân tích hệ thống với {total_docs} tài liệu", {'stats': stats}
                        )
                        if ai_insight:
                            message_text += f"\n\n🤖 **AI Insight:**\n{ai_insight}"
                    except Exception as e:
                        logger.warning(f"AI enhancement failed: {e}")
                
                return {
                    'message': message_text,
                    'type': 'azure_stats',
                    'data': stats,
                    'suggestions': ['Upload hóa đơn mới', 'Hỏi về hóa đơn', 'Tìm kiếm', 'Phân tích']
                }
            else:
                logger.warning(f"Backend API returned {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Cannot connect to backend API: {e}")
        except Exception as e:
            logger.error(f"❌ Error querying Azure data: {e}")
        
        # FALLBACK
        return {
            'message': '⚠️ **Không thể lấy dữ liệu**\n\nHệ thống chưa kết nối được với backend.\n\n📝 **Kiểm tra:**\n• Backend đang chạy? (port 8000)\n• Azure Storage đã cấu hình?\n• Kết nối mạng ổn định?\n\nVui lòng kiểm tra và thử lại.',
            'type': 'error',
            'suggestions': ['Kiểm tra backend', 'Upload ảnh mới', 'Liên hệ support']
        }

    def handle_invoice_analysis'''

content_new = re.sub(pattern, new_function, content, flags=re.DOTALL)

if content_new != content:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content_new)
    print('✅ Successfully replaced handle_data_query function!')
    print('✅ Now queries Azure Storage via Backend API (port 8000)')
    print('✅ PostgreSQL dependency removed')
else:
    print('❌ Pattern not found - no changes made')
    print('Manual fix may be needed')
