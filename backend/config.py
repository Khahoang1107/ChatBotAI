import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
    
    # Chatbot Settings
    BOT_NAME = "InvoiceBot"
    BOT_DESCRIPTION = "Trợ lý AI hỗ trợ xử lý hóa đơn và tư vấn khách hàng"
    
    # Model Settings
    DEFAULT_MODEL = "gpt-3.5-turbo"
    MAX_TOKENS = 1000
    TEMPERATURE = 0.7
    
    # Database Settings
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///chatbot.db')
    
    # Backend API Settings
    BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')  # ⭐ FastAPI backend URL
    
    # Redis Settings (for session management)
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = 'chatbot.log'
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = 30
    
    # Features
    ENABLE_VOICE = True
    ENABLE_IMAGE_ANALYSIS = True
    ENABLE_DOCUMENT_SEARCH = True
    
    # Invoice Processing
    INVOICE_KEYWORDS = [
        'hóa đơn', 'invoice', 'bill', 'receipt',
        'thanh toán', 'payment', 'tiền', 'money',
        'mã số thuế', 'tax code', 'VAT', 'thuế'
    ]
    
    # Response Templates
    GREETING_MESSAGES = [
        "Xin chào! Tôi là {bot_name}, trợ lý AI của bạn.",
        "Chào bạn! Tôi có thể giúp gì cho bạn về hóa đơn hôm nay?",
        "Hi! Tôi sẵn sàng hỗ trợ bạn xử lý các vấn đề về hóa đơn."
    ]
    
    ERROR_MESSAGES = [
        "Xin lỗi, tôi không hiểu câu hỏi của bạn. Bạn có thể nói rõ hơn không?",
        "Tôi cần thêm thông tin để có thể trả lời chính xác. Bạn có thể cung cấp thêm chi tiết không?",
        "Hmm, câu hỏi này hơi khó với tôi. Bạn có thể thử hỏi theo cách khác không?"
    ]