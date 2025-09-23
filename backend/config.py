import os
from datetime import timedelta

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
    
    # Database settings
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///invoice_app.db'
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
    
    # OCR settings
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    OCR_CONFIDENCE_THRESHOLD = 0.8
    OCR_MAX_RETRIES = 3
    
    # MongoDB settings for AI training data
    MONGODB_URL = os.environ.get('MONGODB_URL') or 'mongodb://localhost:27017/'
    MONGODB_DB_NAME = os.environ.get('MONGODB_DB_NAME') or 'invoice_ai_training'
    MONGODB_COLLECTION_TRAINING = 'invoice_training_data'
    MONGODB_COLLECTION_PATTERNS = 'field_patterns'
    
    # Email settings (for notifications)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # API settings
    API_TITLE = 'Invoice Management API'
    API_VERSION = 'v1'
    OPENAPI_VERSION = '3.0.3'
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'memory://'
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    
    # CORS settings
    CORS_ORIGINS = [
        'http://localhost:3000',
        'http://localhost:5174',
        'http://localhost:8080'
    ]
    
    # Pagination
    ITEMS_PER_PAGE = 20
    MAX_ITEMS_PER_PAGE = 100

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev_invoice_app.db'

class ProductionConfig(Config):
    DEBUG = False
    # Use environment variables for production
    
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test_invoice_app.db'
    WTF_CSRF_ENABLED = False

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}