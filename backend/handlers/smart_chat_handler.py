"""
🤖 SMART CHAT HANDLER - Thông minh, trả lời mọi câu hỏi
======================================================

Nâng cấp từ pattern-based → LLM-based chat

Features:
✅ Trả lời mọi câu hỏi (không cần hardcode patterns)
✅ Hiểu ngữ cảnh conversation
✅ Có tri thức về hóa đơn/thuế
✅ Kiểm tra invoice data thực
✅ 3 LLM options: OpenAI (GPT-4) / Groq (FREE) / Ollama (Local)
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import requests

logger = logging.getLogger(__name__)

# Import database tools
try:
    from utils.database_tools import get_database_tools
    db_tools = get_database_tools()
    logger.info("✅ Database tools loaded for Smart Chat")
except Exception as e:
    logger.warning(f"⚠️ Database tools not available: {e}")
    db_tools = None


class SmartChatHandler:
    """
    🧠 Smart Chat with LLM
    Tự động trả lời mọi câu hỏi sử dụng AI
    """
    
    def __init__(self):
        self.llm_provider = os.getenv("LLM_PROVIDER", "groq")  # groq, openai, ollama
        self.llm_api_key = os.getenv("LLM_API_KEY", "")
        self.conversation_history = {}  # {user_id: [messages]}
        self.max_history = 10  # Keep last 10 messages
        
        logger.info(f"🤖 SmartChatHandler initialized with LLM: {self.llm_provider}")
        
        # Initialize LLM client
        self.setup_llm()
    
    def setup_llm(self):
        """Setup LLM provider"""
        if self.llm_provider == "openai":
            try:
                import openai
                openai.api_key = self.llm_api_key
                self.llm_client = openai
                logger.info("✅ OpenAI initialized")
            except Exception as e:
                logger.error(f"❌ OpenAI setup failed: {e}")
                self.llm_client = None
        
        elif self.llm_provider == "groq":
            # Groq doesn't need special setup, just HTTP requests
            self.llm_client = "groq"
            logger.info("✅ Groq initialized")
        
        elif self.llm_provider == "ollama":
            # Ollama runs locally
            self.llm_client = "ollama"
            logger.info("✅ Ollama initialized (local)")
        
        else:
            logger.warning(f"Unknown LLM provider: {self.llm_provider}")
            self.llm_client = None
    
    async def process_message(
        self, 
        message: str, 
        user_id: str = "anonymous",
        context_data: Dict = None
    ) -> Dict[str, Any]:
        """
        🧠 Process user message và trả lời thông minh
        
        Args:
            message: Tin nhắn từ user
            user_id: ID của user (để track conversation history)
            context_data: Dữ liệu context (invoices, templates, etc)
        
        Returns:
            {
                'message': 'AI response',
                'type': 'text',
                'confidence': 0.95,
                'data': {...}  # Nếu có data extracted
            }
        """
        
        try:
            logger.info(f"🤖 Processing message: {message[:100]}...")
            
            # 1. Get conversation history
            history = self.get_conversation_history(user_id)
            
            # 2. Build system prompt với domain knowledge
            system_prompt = self.build_system_prompt(context_data or {})
            
            # 3. Get LLM response
            response = await self.get_llm_response(
                message=message,
                history=history,
                system_prompt=system_prompt,
                context_data=context_data
            )
            
            # 4. Update history
            self.update_history(user_id, message, response)
            
            return {
                "success": True,
                "message": response,
                "type": "text",
                "confidence": 0.95,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return {
                "success": False,
                "message": f"Xin lỗi, đã có lỗi: {str(e)}",
                "type": "text"
            }
    
    def build_system_prompt(self, context_data: Dict) -> str:
        """
        Xây dựng system prompt với domain knowledge + REAL OCR DATA
        """
        
        base_prompt = """Bạn là một trợ lý AI chuyên gia về hóa đơn và thuế tại Việt Nam.

Hành vi:
1. Luôn trả lời Tiếng Việt tự nhiên, thân thiện
2. Giải thích rõ ràng, chi tiết
3. Nếu cần, cung cấp ví dụ cụ thể
4. Nếu không chắc chắn, hãy thừa nhận
5. **ĐẶC BIỆT: Khi user hỏi về hóa đơn, sử dụng dữ liệu OCR THỰC từ database**

Kiến thức:
- Hóa đơn GTGT (VAT), hóa đơn bán hàng
- Mã số thuế, MST cá nhân/doanh nghiệp
- Hóa đơn điện, nước, viễn thông
- Kế toán, báo cáo tài chính cơ bản
- Luật thuế hiện hành Việt Nam"""
        
        # 📊 QUERY DATABASE FOR REAL OCR DATA
        if db_tools:
            try:
                # Get all invoices from database
                all_invoices = db_tools.get_all_invoices(limit=10)
                
                if all_invoices:
                    base_prompt += f"\n\n📋 **DỮ LIỆU HÓA ĐƠN THỰC TỪ DATABASE ({len(all_invoices)} hóa đơn):**"
                    
                    for inv in all_invoices:
                        base_prompt += f"\n- **{inv.get('filename', 'N/A')}**"
                        base_prompt += f"\n  • Mã HĐ: {inv.get('invoice_code', 'N/A')}"
                        base_prompt += f"\n  • Loại: {inv.get('invoice_type', 'N/A')}"
                        base_prompt += f"\n  • Khách: {inv.get('buyer_name', 'N/A')}"
                        base_prompt += f"\n  • Người bán: {inv.get('seller_name', 'N/A')}"
                        base_prompt += f"\n  • Tổng: {inv.get('total_amount', 'N/A')}"
                        
                        # ✅ Convert confidence_score to float (stored as string in DB)
                        try:
                            confidence = float(inv.get('confidence_score', 0))
                            if confidence < 1:
                                confidence = confidence * 100
                            confidence_str = f"{confidence:.1f}%"
                        except (ValueError, TypeError):
                            confidence_str = "N/A"
                        base_prompt += f"\n  • Độ tin cậy: {confidence_str}"
                        
                        # Include raw OCR text if available
                        if inv.get('raw_text'):
                            raw_text = str(inv.get('raw_text', ''))[:200]
                            base_prompt += f"\n  • Nội dung OCR: {raw_text}..."
                    
                    base_prompt += "\n\n⚠️ **Khi user hỏi về hóa đơn, hãy tham khảo dữ liệu THỰC này thay vì tạo dữ liệu giả**"
                else:
                    base_prompt += "\n\n📊 Hiện chưa có hóa đơn nào trong database."
                    
            except Exception as e:
                logger.warning(f"⚠️ Could not load invoice data: {e}")
        
        # Add context from request if available
        if context_data:
            invoices = context_data.get("invoices", [])
            templates = context_data.get("templates", [])
            files = context_data.get("files", [])
            
            if files:
                base_prompt += f"\n\n📁 **Files được upload ({len(files)} files):**"
                for f in files[:5]:
                    base_prompt += f"\n- {f.get('name', 'N/A')} ({f.get('size', 0)} bytes)"
        
        return base_prompt
    
    async def get_llm_response(
        self,
        message: str,
        history: List[Dict],
        system_prompt: str,
        context_data: Dict = None
    ) -> str:
        """
        Gọi LLM để lấy response
        """
        
        if self.llm_provider == "openai":
            return await self._call_openai(message, history, system_prompt)
        elif self.llm_provider == "groq":
            return await self._call_groq(message, history, system_prompt)
        elif self.llm_provider == "ollama":
            return await self._call_ollama(message, history, system_prompt)
        else:
            return "Không có LLM provider nào được cấu hình"
    
    async def _call_openai(self, message: str, history: List, system_prompt: str) -> str:
        """
        Gọi OpenAI API (GPT-4 hoặc GPT-3.5-turbo)
        
        Giá:
        - GPT-3.5-turbo: $0.50 / 1M tokens (~$0.001 / message)
        - GPT-4: $0.03 / 1K tokens (~$0.03-0.05 / message)
        """
        try:
            import openai
            
            # Build messages
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add conversation history
            for msg in history[-5:]:  # Last 5 messages
                messages.append({"role": "user", "content": msg["user"]})
                messages.append({"role": "assistant", "content": msg["assistant"]})
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Call API
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",  # or gpt-4
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"❌ OpenAI error: {e}")
            return f"Lỗi khi gọi OpenAI: {str(e)}"
    
    async def _call_groq(self, message: str, history: List, system_prompt: str) -> str:
        """
        Gọi Groq API (FREE, nhanh hơn OpenAI)
        
        Groq là provider MIỄN PHÍ, không giới hạn requests
        Model: llama-3.3-70b-versatile (LLaMA 3.3 70B - hiện tại được hỗ trợ)
        
        ⭐ THÊM: Tích hợp FastAPI để gọi camera và xem hóa đơn
        """
        try:
            if not self.llm_api_key:
                return "❌ Chưa cấu hình GROQ_API_KEY"
            
            # 🎬 KIỂM TRA Intent: Mở camera hoặc xem hóa đơn
            action_result = self._check_for_fastapi_actions(message)
            if action_result:
                return action_result
            
            # Build messages - ensure all content is strings
            messages = [
                {"role": "system", "content": str(system_prompt).strip()}
            ]
            
            # Add conversation history
            for msg in history[-5:]:
                user_content = str(msg.get("user", "")).strip()
                assistant_content = str(msg.get("assistant", "")).strip()
                if user_content:
                    messages.append({"role": "user", "content": user_content})
                if assistant_content:
                    messages.append({"role": "assistant", "content": assistant_content})
            
            # Add current message
            current_message = str(message).strip()
            if current_message:
                messages.append({"role": "user", "content": current_message})
            
            # Validate messages
            if len(messages) < 2:
                return "❌ Không có nội dung để xử lý"
            
            # Log for debugging
            logger.info(f"📤 Groq API - Model: llama-3.3-70b-versatile, Messages: {len(messages)}")
            
            # Call Groq API using groq SDK (more reliable)
            try:
                from groq import Groq
                client = Groq(api_key=self.llm_api_key)
                
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=500,
                    top_p=1,
                    stream=False
                )
                
                result = response.choices[0].message.content
                logger.info(f"✅ Groq response: {len(result)} chars")
                return result
                
            except Exception as sdk_error:
                logger.warning(f"⚠️  Groq SDK error: {sdk_error}, falling back to httpx")
                
                # Fallback to httpx
                import httpx
                async with httpx.AsyncClient(timeout=15) as client:
                    payload = {
                        "model": "llama-3.3-70b-versatile",
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 500
                    }
                    
                    logger.info(f"📨 Groq httpx payload: {payload}")
                    
                    response = await client.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.llm_api_key}",
                            "Content-Type": "application/json"
                        },
                        json=payload
                    )
                
                logger.info(f"Groq response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    error_text = response.text
                    logger.error(f"Groq error: {response.status_code} - {error_text}")
                    return f"❌ Lỗi Groq: {response.status_code} - {error_text[:100]}"
        
        except Exception as e:
            logger.error(f"❌ Groq error: {type(e).__name__}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return f"Lỗi khi gọi Groq: {str(e)}"
    
    def _check_for_fastapi_actions(self, message: str) -> Optional[str]:
        """
        🎬 Kiểm tra message có yêu cầu:
        - Mở/đóng camera
        - Xem danh sách hóa đơn
        - Xuất danh sách hóa đơn
        
        Nếu có, gọi FastAPI backend thay vì Groq
        """
        message_lower = message.lower()
        
        # 📷 CLOSE CAMERA ACTIONS - Check này trước để ưu tiên
        close_camera_keywords = [
            'đóng camera', 'dong camera', 'đóng máy ảnh', 'dong may anh',
            'tắt camera', 'tat camera', 'tắt máy ảnh', 'tat may anh',
            'close camera', 'turn off camera', 'stop camera',
            'lưu ảnh', 'luu anh',  # Save photo - implies closing
            'xong', 'done'  # Vietnamese way of saying done/finished
        ]
        if any(kw in message_lower for kw in close_camera_keywords):
            logger.info(f"🎬 Close camera action detected: {message}")
            return self._handle_close_camera_action(message)
        
        # 📷 OPEN CAMERA ACTIONS
        camera_keywords = ['mở camera', 'open camera', 'camera', 'chụp ảnh', 'take photo', 'photo', 'máy ảnh', 'bật camera', 'bat camera']
        if any(kw in message_lower for kw in camera_keywords):
            logger.info(f"🎬 Open camera action detected: {message}")
            return self._handle_camera_action(message)
        
        # 📥 EXPORT ACTIONS
        export_keywords = ['xuất', 'export', 'download', 'tải', 'lưu file', 'save', 'lấy danh sách']
        if any(kw in message_lower for kw in export_keywords):
            logger.info(f"📥 Export action detected: {message}")
            return self._handle_export_action(message)
        
        # 📋 INVOICE LIST ACTIONS
        invoice_keywords = ['danh sách hóa đơn', 'xem hóa đơn', 'invoice list', 'list invoice', 'hóa đơn', 'hóa đơn hôm nay', 'hóa đơn ngày', 'invoices']
        if any(kw in message_lower for kw in invoice_keywords):
            logger.info(f"📋 Invoice action detected: {message}")
            return self._handle_invoice_list_action(message)
        
        return None
    
    def _handle_camera_action(self, message: str) -> str:
        """📷 Xử lý yêu cầu mở camera"""
        try:
            logger.info(f"📷 Camera action: {message}")
            
            # Trả về thông báo đặc biệt cho frontend để mở camera
            # Format: [CAMERA_OPEN] để frontend nhận diện
            camera_message = "[CAMERA_OPEN]\n\n📷 **Mở camera thành công!**\n\n🎥 Máy ảnh đã sẵn sàng. Bạn có thể:\n• Chụp ảnh hóa đơn\n• Quét mã QR\n• Ghi video\n\nSau khi chụp xong, hãy nhấn 'Lưu' để xử lý OCR hoặc nói 'đóng camera'."
            
            logger.info(f"✅ Camera opened successfully")
            return camera_message
        
        except Exception as e:
            logger.warning(f"⚠️ Camera error: {e}")
            return f"❌ Lỗi mở camera: {str(e)}\n\nVui lòng thử lại."
    
    def _handle_close_camera_action(self, message: str) -> str:
        """📷 Xử lý yêu cầu đóng camera"""
        try:
            logger.info(f"📷 Close camera action: {message}")
            
            # Trả về thông báo đặc biệt cho frontend để đóng camera
            # Format: [CAMERA_CLOSE] để frontend nhận diện
            close_message = "[CAMERA_CLOSE]\n\n📷 **Camera đã đóng.**\n\nBạn có thể:\n• Mở camera lại để chụp thêm\n• Xem danh sách hóa đơn\n• Hỏi tôi về tài liệu\n\nBạn muốn làm gì tiếp theo?"
            
            logger.info(f"✅ Camera closed successfully")
            return close_message
        
        except Exception as e:
            logger.warning(f"⚠️ Close camera error: {e}")
            return f"❌ Lỗi đóng camera: {str(e)}\n\nVui lòng thử lại."
    
    def _handle_invoice_list_action(self, message: str) -> str:
        """📋 Xử lý yêu cầu xem danh sách hóa đơn - query database + FastAPI"""
        try:
            # Kiểm tra ngày nếu user hỏi theo ngày
            if 'hôm nay' in message.lower():
                time_filter = 'today'
            elif 'hôm qua' in message.lower():
                time_filter = 'yesterday'
            elif 'tuần' in message.lower():
                time_filter = 'week'
            elif 'tháng' in message.lower():
                time_filter = 'month'
            else:
                time_filter = 'all'
            
            logger.info(f"📋 Getting invoices with time filter: {time_filter}")
            
            # Nếu có database tools, query database trực tiếp
            if db_tools:
                invoices = db_tools.get_all_invoices(limit=20)
                
                if not invoices:
                    return "❌ Không có hóa đơn nào trong hệ thống.\n\nVui lòng upload ảnh hóa đơn để bắt đầu."
                
                # Format danh sách hóa đơn
                result = f"📋 **Danh sách hóa đơn ({len(invoices)} hóa đơn)**\n\n"
                
                for i, inv in enumerate(invoices[:10], 1):
                    # ✅ Convert confidence_score to float (stored as string in DB)
                    try:
                        confidence = float(inv.get('confidence_score', 0))
                        # If confidence < 1, multiply by 100 (e.g., 0.95 -> 95%)
                        if confidence < 1:
                            confidence = confidence * 100
                        confidence_str = f"{confidence:.1f}%"
                    except (ValueError, TypeError):
                        confidence_str = "N/A"
                    
                    result += f"{i}. **{inv.get('filename', 'N/A')}**\n"
                    result += f"   • Mã HĐ: `{inv.get('invoice_code', 'N/A')}`\n"
                    result += f"   • Loại: {inv.get('invoice_type', 'N/A')}\n"
                    result += f"   • Khách: {inv.get('buyer_name', 'N/A')}\n"
                    result += f"   • Tổng tiền: **{inv.get('total_amount', 'N/A')}**\n"
                    result += f"   • Độ tin cậy: {confidence_str}\n"
                    result += f"   • Ngày: {inv.get('invoice_date', 'N/A')}\n\n"
                
                result += "💡 **Bạn muốn làm gì tiếp theo?**\n"
                result += "• Xem chi tiết một hóa đơn: 'Xem hóa đơn [số]'\n"
                result += "• Tìm kiếm: 'Tìm hóa đơn [từ khóa]'\n"
                result += "• Thống kê: 'Thống kê hóa đơn'\n"
                result += "• Upload thêm: 'Mở camera' hoặc 'Upload ảnh'"
                
                logger.info(f"✅ Returned {len(invoices)} invoices from database")
                return result
            else:
                return "⚠️ Không thể kết nối với database hóa đơn. Vui lòng kiểm tra kết nối PostgreSQL."
        
        except Exception as e:
            logger.error(f"❌ Invoice list error: {e}")
            return f"❌ Lỗi khi lấy danh sách hóa đơn: {str(e)}\n\nVui lòng thử lại."
    
    def _handle_export_action(self, message: str) -> str:
        """
        📥 Xử lý yêu cầu xuất hóa đơn
        
        Hỗ trợ các định dạng:
        - Excel (.xlsx)
        - CSV (.csv)
        - PDF (.pdf)
        - JSON (.json)
        
        Hỗ trợ các bộ lọc:
        - Theo ngày: "xuất hóa đơn ngày 19/10"
        - Theo tháng: "xuất hóa đơn tháng 10"
        - Khoảng thời gian: "xuất hóa đơn từ 1/10 đến 31/10"
        """
        try:
            import re
            from datetime import datetime
            import httpx
            
            message_lower = message.lower()
            
            # 🔍 Xác định định dạng xuất (mặc định Excel)
            export_format = "excel"
            if "csv" in message_lower:
                export_format = "csv"
            elif "pdf" in message_lower:
                export_format = "pdf"
            elif "json" in message_lower:
                export_format = "json"
            
            # Tìm ngày/tháng trong message
            today = datetime.now()
            start_date = None
            end_date = None
            month = None
            year = None
            
            # ✅ Tìm kiếm "ngày dd/mm" hoặc "ngày dd-mm"
            date_pattern = r'ngày\s+(\d{1,2})[/-](\d{1,2})'
            date_match = re.search(date_pattern, message_lower)
            
            if date_match:
                day = int(date_match.group(1))
                month_num = int(date_match.group(2))
                year = today.year if month_num >= today.month else today.year
                start_date = f"{year:04d}-{month_num:02d}-{day:02d}"
                logger.info(f"📅 Found date: {start_date}")
            
            # ✅ Tìm kiếm "tháng mm" hoặc "tháng mm/yyyy"
            month_pattern = r'tháng\s+(\d{1,2})(?:[/-](\d{4}))?'
            month_match = re.search(month_pattern, message_lower)
            
            if month_match:
                month = int(month_match.group(1))
                year = int(month_match.group(2)) if month_match.group(2) else today.year
                logger.info(f"📅 Found month: {year}-{month:02d}")
            
            # ✅ Tìm kiếm "hôm nay", "hôm qua", "tuần này", "tháng này"
            if "hôm nay" in message_lower or "today" in message_lower:
                start_date = today.strftime("%Y-%m-%d")
                logger.info(f"📅 Today: {start_date}")
            
            elif "hôm qua" in message_lower:
                yesterday = today - __import__("datetime").timedelta(days=1)
                start_date = yesterday.strftime("%Y-%m-%d")
                logger.info(f"📅 Yesterday: {start_date}")
            
            elif "tuần này" in message_lower or "this week" in message_lower:
                # Lấy từ thứ Hai của tuần này
                monday = today - __import__("datetime").timedelta(days=today.weekday())
                start_date = monday.strftime("%Y-%m-%d")
                end_date = today.strftime("%Y-%m-%d")
                logger.info(f"📅 This week: {start_date} to {end_date}")
            
            elif "tháng này" in message_lower or "this month" in message_lower:
                month = today.month
                year = today.year
                logger.info(f"📅 This month: {year}-{month:02d}")
            
            # 🔗 Gọi FastAPI backend
            logger.info(f"📥 Preparing export: format={export_format}, date={start_date}, month={month}")
            
            params = {}
            endpoint = None
            
            if month is not None and start_date is None:
                # Xuất theo tháng
                endpoint = f"http://localhost:8000/api/export/by-month/{export_format}"
                params = {"year": year, "month": month}
            
            elif start_date and end_date:
                # Xuất theo khoảng thời gian
                endpoint = f"http://localhost:8000/api/export/by-range/{export_format}"
                params = {"start_date": start_date, "end_date": end_date}
            
            elif start_date:
                # Xuất theo ngày
                endpoint = f"http://localhost:8000/api/export/by-date/{export_format}"
                params = {"date": start_date}
            
            else:
                # Nếu không tìm thấy ngày, dùng tháng hiện tại
                endpoint = f"http://localhost:8000/api/export/by-month/{export_format}"
                params = {"year": today.year, "month": today.month}
                logger.info(f"📅 Default to current month: {today.year}-{today.month:02d}")
            
            logger.info(f"📥 Calling export endpoint: {endpoint} with params: {params}")
            
            # Gọi endpoint
            response = httpx.post(endpoint, params=params, timeout=30)
            
            if response.status_code == 200:
                file_size = len(response.content)
                
                # Xác định tên file
                if month is not None and not end_date:
                    filename = f"hoá_đơn_{year}_{month:02d}.{export_format if export_format != 'excel' else 'xlsx'}"
                    time_desc = f"tháng {month}/{year}"
                elif end_date:
                    filename = f"hoá_đơn_{start_date}_đến_{end_date}.{export_format if export_format != 'excel' else 'xlsx'}"
                    time_desc = f"từ {start_date} đến {end_date}"
                else:
                    filename = f"hoá_đơn_{start_date}.{export_format if export_format != 'excel' else 'xlsx'}"
                    time_desc = f"ngày {start_date}"
                
                return f"""✅ **Xuất hóa đơn thành công!**

📋 **Chi tiết:**
• Thời gian: {time_desc}
• Định dạng: {export_format.upper()}
• Kích thước file: {file_size:,} bytes
• Tên file: `{filename}`

📥 **File đã sẵn sàng để tải xuống!**

💡 **Gợi ý tiếp theo:**
• Nếu bạn muốn xuất ngày khác, cứ nói: "Xuất hóa đơn ngày 15/10"
• Hoặc: "Xuất hóa đơn tháng 9"
• Hoặc: "Xuất hóa đơn từ 1/10 đến 31/10"
"""
            
            elif response.status_code == 404:
                data = response.json()
                return f"⚠️ **Không tìm thấy dữ liệu**\n\nKhông có hóa đơn nào trong khoảng thời gian bạn chọn.\n\nThông báo: {data.get('detail', 'Unknown')}"
            
            else:
                return f"❌ **Lỗi xuất hóa đơn** (Code {response.status_code})\n\nVui lòng thử lại hoặc liên hệ quản trị viên."
        
        except Exception as e:
            logger.error(f"❌ Export error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return f"❌ Lỗi khi xuất hóa đơn: {str(e)}\n\nVui lòng kiểm tra lại yêu cầu."
    
    async def _call_ollama(self, message: str, history: List, system_prompt: str) -> str:
        """
        Gọi Ollama (chạy local, MIỄN PHÍ, không cần API key)
        
        Setup:
        1. Download Ollama: https://ollama.ai
        2. Chạy: ollama run llama2-vietnamese
        3. Mặc định port 11434
        """
        try:
            # Build messages
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add conversation history
            for msg in history[-5:]:
                messages.append({"role": "user", "content": msg["user"]})
                messages.append({"role": "assistant", "content": msg["assistant"]})
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Call Ollama
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:11434/api/chat",
                    json={
                        "model": "llama2-vietnamese",  # or llama2, mistral, etc
                        "messages": messages,
                        "stream": False
                    },
                    timeout=30
                )
            
            if response.status_code == 200:
                data = response.json()
                return data["message"]["content"]
            else:
                logger.error(f"Ollama error: {response.status_code}")
                return f"Lỗi Ollama: {response.status_code}"
        
        except Exception as e:
            logger.error(f"❌ Ollama error: {e}")
            return f"Lỗi khi gọi Ollama (chắc chắn đã chạy ollama serve chưa?): {str(e)}"
    
    def get_conversation_history(self, user_id: str) -> List[Dict]:
        """Lấy lịch sử conversation của user"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        return self.conversation_history[user_id]
    
    def update_history(self, user_id: str, user_message: str, assistant_message: str):
        """Cập nhật lịch sử conversation"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            "user": user_message,
            "assistant": assistant_message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last N messages to save memory
        if len(self.conversation_history[user_id]) > self.max_history:
            self.conversation_history[user_id] = self.conversation_history[user_id][-self.max_history:]


# Global instance
smart_chat_handler = SmartChatHandler()
