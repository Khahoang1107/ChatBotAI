"""
Groq Chat Handler with Database API Integration
Groq thao tác với database thông qua API tools
"""

import json
import logging
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from decimal import Decimal
from groq import Groq

logger = logging.getLogger(__name__)

class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal and datetime objects"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)

class GroqChatHandler:
    """
    Groq Chat Handler với khả năng gọi API để thao tác database
    
    Flow:
    1. User gửi message
    2. Groq analyze intent + chọn tools cần thiết
    3. Groq gọi API tools để lấy data từ database
    4. Groq combine data + sinh response
    """
    
    def __init__(self, db_tools=None, groq_tools=None):
        """Initialize Groq handler with database tools"""
        # Get API key from environment
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            logger.warning("⚠️ GROQ_API_KEY not found in environment")
            self.client = None
        else:
            self.client = Groq(api_key=api_key)
        
        self.db_tools = db_tools
        self.groq_tools = groq_tools
        self.conversation_history = {}
        self.model = "llama-3.3-70b-versatile"
        self.db_tools = db_tools
        self.groq_tools = groq_tools
        self.conversation_history = {}
        self.model = "llama-3.3-70b-versatile"
        
        # Store recent OCR results for saving
        self.recent_ocr_results = {}
        
        # Import services
        try:
            from utils.sentiment_service import sentiment_service
            from utils.conversation_service import conversation_service
            self.sentiment_service = sentiment_service
            self.conversation_service = conversation_service
        except ImportError:
            self.sentiment_service = None
            self.conversation_service = None
        
        # Build tools description for system prompt
        tools_desc = ""
        if groq_tools:
            for tool in groq_tools.get_tools_description():
                tools_desc += f"\n- {tool['name']}: {tool['description']}"
        
        # System prompt với tools
        self.system_prompt = f"""Bạn là trợ lý AI thông minh cho hệ thống quản lý hóa đơn.

Nhiệm vụ:
1. Phân tích yêu cầu của người dùng
2. SỬ DỤNG các tools có sẵn để lấy dữ liệu từ database HOẶC lưu dữ liệu
3. Xử lý, phân tích dữ liệu
4. Trả lời chính xác và hữu ích

Quy tắc QUAN TRỌNG:
- Luôn gọi tools để lấy dữ liệu thực tế (đừng đoán)
- Khi cần lấy dữ liệu, hãy nói: "Tôi sẽ sử dụng tool [tool_name] để..."
- Khi người dùng muốn LƯU HÓA ĐƠN từ OCR, hãy sử dụng tool save_invoice_from_ocr
- Sau khi gọi tool, phân tích kết quả và trả lời
- Trả lời bằng Tiếng Việt
- Luôn cung cấp dữ liệu thực từ database

XỬ LÝ LỆNH LƯU HÓA ĐƠN:
- Khi người dùng nói "lưu hóa đơn", "save invoice", "lưu vào database" -> sử dụng tool save_invoice_from_ocr
- Tool này cần dữ liệu OCR đã extract (invoice_code, buyer_name, total_amount, etc.)
- Nếu chưa có dữ liệu OCR, hãy hỏi người dùng upload ảnh trước

Các tools có sẵn:{tools_desc}

CÁCH SỬ DỤNG: Khi bạn cần lấy dữ liệu, hãy nói rõ:
1. "Tôi sẽ lấy dữ liệu bằng tool: [tool_name]"
2. Mô tả kết quả bạn nhận được
3. Trả lời câu hỏi dựa trên dữ liệu

Đối với lưu hóa đơn:
1. "Tôi sẽ lưu hóa đơn bằng tool: save_invoice_from_ocr"
2. Mô tả kết quả lưu trữ
3. Thông báo thành công cho người dùng"""
    
    async def chat(self, message: str, user_id: str = 'default') -> Dict[str, Any]:
        """
        Main chat method - Groq sử dụng tools để trả lời
        
        Args:
            message: User message
            user_id: User ID for tracking
        
        Returns:
            Chat response with metadata
        """
        try:
            # Analyze sentiment
            sentiment, sentiment_confidence = ('neutral', 0.5)
            if self.sentiment_service:
                sentiment, sentiment_confidence = self.sentiment_service.analyze_sentiment(message)
            
            # Get conversation history from database if user_id is numeric (authenticated user)
            conversation_context = []
            if user_id.isdigit() and self.conversation_service:
                try:
                    user_id_int = int(user_id)
                    # Generate session_id from user_id (simple approach)
                    session_id = f"user_{user_id}"
                    conversation_context = self.conversation_service.get_conversation_history(user_id_int, session_id, limit=20)
                except Exception as e:
                    logger.warning(f"Could not load conversation history: {e}")
            
            # Update conversation history
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            
            # Thêm user message vào history
            self.conversation_history[user_id].append({
                "role": "user",
                "content": message
            })
            
            # Get tools descriptions from Groq tools
            if self.groq_tools:
                tools_description = self.groq_tools.get_tools_description()
            else:
                tools_description = []
            
            # Tạo message cho Groq với tools
            response = await self._groq_with_tools(
                message=message,
                user_id=user_id,
                tools_description=tools_description,
                sentiment=sentiment,
                conversation_context=conversation_context
            )
            
            # Adjust response based on sentiment
            if self.sentiment_service and sentiment == 'negative':
                response['message'] = self.sentiment_service.adjust_response_based_on_sentiment(sentiment, response['message'])
            
            # Add bot response to history
            self.conversation_history[user_id].append({
                "role": "assistant",
                "content": response['message']
            })
            
            # Save to database if authenticated user
            if user_id.isdigit() and self.conversation_service:
                try:
                    user_id_int = int(user_id)
                    session_id = f"user_{user_id}"
                    
                    # Save user message
                    self.conversation_service.save_message(
                        user_id_int, session_id, 'user', message,
                        {'sentiment': sentiment, 'sentiment_confidence': sentiment_confidence}
                    )
                    
                    # Save bot response
                    self.conversation_service.save_message(
                        user_id_int, session_id, 'bot', response['message'],
                        {'method': response.get('method', 'groq')}
                    )
                    
                except Exception as e:
                    logger.warning(f"Could not save conversation to database: {e}")
            
            # Keep only last 20 exchanges
            if len(self.conversation_history[user_id]) > 40:
                self.conversation_history[user_id] = self.conversation_history[user_id][-40:]
            
            # Add sentiment info to response
            response['sentiment'] = sentiment
            response['sentiment_confidence'] = sentiment_confidence
            
            return response
            
        except Exception as e:
            logger.error(f"Error in Groq chat: {str(e)}")
            return self._error_response(str(e))
    
    async def chat_stream(self, message: str, user_id: str = 'default'):
        """
        Stream chat response from Groq (real-time, word-by-word)
        
        Usage in FastAPI:
        @app.post("/chat/groq/stream")
        async def chat_groq_stream(request: ChatMessageRequest):
            return StreamingResponse(
                groq_chat_handler.chat_stream(request.message, request.user_id),
                media_type="application/x-ndjson"
            )
        """
        try:
            # Update conversation history
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            
            # Add user message to history
            self.conversation_history[user_id].append({
                "role": "user",
                "content": message
            })
            
            # Get tools descriptions
            if self.groq_tools:
                tools_description = self.groq_tools.get_tools_description()
            else:
                tools_description = []
            
            # Stream the response
            full_response = ""
            async for chunk in self._groq_stream_with_tools(message, user_id, tools_description):
                full_response += chunk
                # Yield as NDJSON (newline-delimited JSON)
                yield json.dumps({
                    "type": "content",
                    "text": chunk,
                    "timestamp": datetime.now().isoformat()
                }) + "\n"
            
            # Add final response to history
            self.conversation_history[user_id].append({
                "role": "assistant",
                "content": full_response
            })
            
            # Keep only last 20 exchanges
            if len(self.conversation_history[user_id]) > 40:
                self.conversation_history[user_id] = self.conversation_history[user_id][-40:]
            
            # Yield completion signal
            yield json.dumps({
                "type": "done",
                "timestamp": datetime.now().isoformat()
            }) + "\n"
            
        except Exception as e:
            logger.error(f"Error in Groq stream: {str(e)}", exc_info=True)
            yield json.dumps({
                "type": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }) + "\n"
    
    async def _groq_stream_with_tools(self, message: str, user_id: str, tools_description: List[Dict]):
        """
        Internal streaming method - uses streaming API from Groq
        """
        try:
            messages = self.conversation_history.get(user_id, []).copy()
            max_iterations = 3
            iteration = 0
            
            while iteration < max_iterations:
                iteration += 1
                
                # Use streaming API
                stream = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        *messages
                    ],
                    temperature=0.7,
                    max_tokens=1000,
                    stream=True  # ← Enable streaming
                )
                
                full_response = ""
                
                # Stream chunks from Groq
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        text = chunk.choices[0].delta.content
                        full_response += text
                        yield text
                
                logger.info(f"Groq stream iteration {iteration}: {full_response[:100]}")
                
                # Check if tools were used
                tool_used = False
                for tool in tools_description:
                    tool_name = tool['name']
                    if tool_name in full_response.lower():
                        tool_used = True
                        logger.info(f"Groq wants to call tool: {tool_name}")
                        
                        # Call tool based on name
                        if tool_name == "get_all_invoices":
                            result = self.groq_tools.get_all_invoices(limit=10)
                        elif tool_name == "search_invoices":
                            result = self.groq_tools.search_invoices(message, limit=5)
                        elif tool_name == "get_statistics":
                            result = self.groq_tools.get_statistics()
                        elif tool_name == "get_high_value_invoices":
                            result = self.groq_tools.get_high_value_invoices(1000000)
                        elif tool_name == "save_invoice_from_ocr":
                            # Get OCR data from recent results for this user
                            ocr_data = self.get_recent_ocr_result(user_id)
                            if ocr_data:
                                result = self.groq_tools.save_invoice_from_ocr(ocr_data=ocr_data)
                            else:
                                result = {"success": False, "error": "Không có dữ liệu OCR gần đây. Vui lòng upload ảnh hóa đơn trước."}
                        else:
                            result = self.groq_tools.call_tool(tool_name)
                        
                        # Add tool result to messages for next iteration
                        messages.append({
                            "role": "assistant",
                            "content": full_response
                        })
                        messages.append({
                            "role": "user",
                            "content": f"Kết quả từ tool {tool_name}: {json.dumps(result, cls=DecimalEncoder)[:500]}"
                        })
                        
                        # Yield tool result notification
                        yield f"\n\n[Tool: {tool_name}]\n"
                        break
                
                if not tool_used:
                    # No more tools needed, we're done
                    break
            
        except Exception as e:
            logger.error(f"Error in Groq stream with tools: {str(e)}", exc_info=True)
            yield f"[ERROR] {str(e)}"
    
    async def _groq_with_tools(self, message: str, user_id: str, tools_description: List[Dict], 
                              sentiment: str = 'neutral', conversation_context: List[Dict] = None) -> Dict[str, Any]:
        """
        Groq gọi tools thông qua Groq Function Calling
        
        Flow:
        1. Groq analyze message + tools -> decide tools cần gọi
        2. Groq return tool_calls JSON
        3. Backend gọi tools từ Groq tool_calls
        4. Groq analyze results -> generate response
        """
        try:
            messages = self.conversation_history.get(user_id, []).copy()
            max_iterations = 5
            iteration = 0
            
            while iteration < max_iterations:
                iteration += 1
                
                # Convert tools_description to Groq format
                groq_tools_format = []
                for tool in tools_description:
                    groq_tools_format.append({
                        "type": "function",
                        "function": {
                            "name": tool['name'],
                            "description": tool['description'],
                            "parameters": tool['parameters']
                        }
                    })
                
                # Build messages with conversation context
                messages = []
                
                # Add system prompt
                system_content = self.system_prompt
                if sentiment == 'negative':
                    system_content += "\n\nLƯU Ý: Người dùng có vẻ không hài lòng. Hãy trả lời một cách thông cảm, hữu ích và chủ động hỗ trợ."
                elif sentiment == 'positive':
                    system_content += "\n\nLƯU Ý: Người dùng có vẻ hài lòng. Hãy duy trì thái độ tích cực và thân thiện."
                
                messages.append({"role": "system", "content": system_content})
                
                # Add conversation history from database
                if conversation_context:
                    for msg in conversation_context[-10:]:  # Last 10 messages for context
                        role = 'user' if msg['message_type'] == 'user' else 'assistant'
                        messages.append({
                            "role": role,
                            "content": msg['message_content']
                        })
                
                # Add current conversation from memory
                for msg in self.conversation_history.get(user_id, [])[-10:]:
                    messages.append(msg)
                
                # Call Groq with tools
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=groq_tools_format if groq_tools_format else None,
                    temperature=0.7,
                    max_tokens=1000
                )
                
                # Get response
                assistant_message = response.choices[0].message
                groq_response_text = assistant_message.content or ""
                
                logger.info(f"Groq iteration {iteration}: {groq_response_text[:100]}")
                
                # Add assistant response to messages
                messages.append({
                    "role": "assistant",
                    "content": groq_response_text
                })
                
                # Check if Groq wants to use tools (function calling)
                tool_calls = getattr(assistant_message, 'tool_calls', None)
                
                if tool_calls:
                    # Groq called one or more tools
                    for tool_call in tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments) if isinstance(tool_call.function.arguments, str) else tool_call.function.arguments
                        
                        logger.info(f"✅ Groq calling tool: {tool_name}({tool_args})")
                        
                        # Call the tool
                        if tool_name == "save_invoice_from_ocr":
                            # For save_invoice_from_ocr, get OCR data from recent results
                            ocr_data = self.get_recent_ocr_result(user_id)
                            if ocr_data:
                                tool_args["ocr_data"] = ocr_data
                                result = self.groq_tools.call_tool(tool_name, **tool_args)
                            else:
                                result = {"success": False, "error": "Không có dữ liệu OCR gần đây. Vui lòng upload ảnh hóa đơn trước."}
                        else:
                            result = self.groq_tools.call_tool(tool_name, **tool_args)
                        
                        logger.info(f"Tool result: {json.dumps(result, cls=DecimalEncoder)[:200]}")
                        
                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "content": json.dumps(result, cls=DecimalEncoder),
                            "tool_call_id": tool_call.id
                        })
                    
                    # Continue loop to let Groq process tool results
                    continue
                else:
                    # Groq didn't call tools, return the final response
                    return {
                        "message": groq_response_text if groq_response_text else "Xin lỗi, tôi không có dữ liệu để trả lời",
                        "type": "text",
                        "method": "groq_function_calling",
                        "iteration": iteration,
                        "timestamp": datetime.now().isoformat()
                    }
            
            # After max iterations, return final response
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    *messages[-6:]  # Last 6 messages
                ],
                temperature=0.7,
                max_tokens=800
            )
            final_message = final_response.choices[0].message.content
            
            return {
                "message": final_message,
                "type": "text",
                "method": "groq_function_calling",
                "iteration": iteration,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in Groq with tools: {str(e)}", exc_info=True)
            return self._error_response(str(e))
    
    async def chat_simple(self, message: str, user_id: str = 'default') -> Dict[str, Any]:
        """
        Chat mà không dùng tools (đơn giản hơn)
        Dùng khi chỉ cần trả lời chung chung
        """
        try:
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            
            # Add to history
            self.conversation_history[user_id].append({
                "role": "user",
                "content": message
            })
            
            # Call Groq without tools
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    *self.conversation_history[user_id]
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            final_message = response.choices[0].message.content
            
            # Add to history
            self.conversation_history[user_id].append({
                "role": "assistant",
                "content": final_message
            })
            
            return {
                "message": final_message,
                "type": "text",
                "method": "groq_simple",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in Groq simple chat: {str(e)}")
            return self._error_response(str(e))
    
    def _error_response(self, error: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "message": "Xin lỗi, tôi gặp lỗi kỹ thuật. Vui lòng thử lại sau.",
            "type": "error",
            "method": "groq",
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
    
    def store_ocr_result(self, user_id: str, ocr_data: dict):
        """
        Store recent OCR result for a user to be used by save_invoice_from_ocr tool
        
        Args:
            user_id: User identifier
            ocr_data: Extracted OCR data from extract_invoice_fields()
        """
        if user_id not in self.recent_ocr_results:
            self.recent_ocr_results[user_id] = []
        
        # Add timestamp and store
        ocr_data['timestamp'] = datetime.now().isoformat()
        self.recent_ocr_results[user_id].append(ocr_data)
        
        # Keep only last 5 OCR results per user
        if len(self.recent_ocr_results[user_id]) > 5:
            self.recent_ocr_results[user_id] = self.recent_ocr_results[user_id][-5:]
        
        logger.info(f"📄 Stored OCR result for user {user_id}: {ocr_data.get('invoice_code', 'UNKNOWN')}")
    
    def get_recent_ocr_result(self, user_id: str) -> dict:
        """
        Get the most recent OCR result for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            Most recent OCR data or empty dict if none available
        """
        if user_id in self.recent_ocr_results and self.recent_ocr_results[user_id]:
            return self.recent_ocr_results[user_id][-1]  # Most recent
        return {}

