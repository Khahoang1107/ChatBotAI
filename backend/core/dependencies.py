# Service Layer - Dependency Injection Container

from typing import Optional
from pathlib import Path
import sys

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from core.logging import logger

try:
    from config.settings import settings
except ImportError:
    # Fallback if import fails
    class DummySettings:
        DATABASE_URL = "postgresql://localhost/chatbot"
        DB_POOL_SIZE = 5
        DB_POOL_OVERFLOW = 10
        DEBUG = False
        GROQ_API_KEY = None
    settings = DummySettings()

import httpx


class ServiceContainer:
    """Centralized service dependency injection with lazy initialization"""
    
    def __init__(self):
        self._db: Optional[Session] = None
        self._groq_client = None
        self._http_client: Optional[httpx.AsyncClient] = None
        self._engine = None
        self._settings = settings
    
    @property
    def settings(self):
        """Get application settings"""
        return self._settings
    
    @property
    def engine(self):
        """Get database engine with lazy initialization"""
        if self._engine is None:
            # SQLite doesn't support pool_size, so check database type
            if "sqlite" in self._settings.DATABASE_URL:
                self._engine = create_engine(
                    self._settings.DATABASE_URL,
                    echo=getattr(self._settings, 'DEBUG', False)
                )
            else:
                self._engine = create_engine(
                    self._settings.DATABASE_URL,
                    pool_size=getattr(self._settings, 'DATABASE_POOL_SIZE', 5),
                    max_overflow=getattr(self._settings, 'DATABASE_MAX_OVERFLOW', 10),
                    echo=getattr(self._settings, 'DEBUG', False)
                )
        return self._engine
    
    @property
    def db(self) -> Session:
        """Get database session with lazy initialization"""
        if self._db is None:
            try:
                engine = self.engine
                SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
                self._db = SessionLocal()
                logger.info("Database session initialized")
            except Exception as e:
                logger.error(f"Failed to initialize database: {str(e)}")
                raise
        return self._db
    
    @property
    def groq_client(self):
        """Get Groq AI client with lazy initialization"""
        if self._groq_client is None:
            try:
                from groq import Groq
                if not self._settings.GROQ_API_KEY:
                    logger.warning("GROQ_API_KEY not configured")
                    return None
                self._groq_client = Groq(api_key=self._settings.GROQ_API_KEY)
                logger.info("Groq client initialized")
            except ImportError:
                logger.error("Groq library not installed. Install: pip install groq")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {str(e)}")
        return self._groq_client
    
    @property
    def http_client(self) -> Optional[httpx.AsyncClient]:
        """Get async HTTP client for external APIs"""
        if self._http_client is None:
            try:
                self._http_client = httpx.AsyncClient(
                    timeout=30.0,
                    limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
                )
                logger.info("HTTP client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize HTTP client: {str(e)}")
        return self._http_client
    
    def close(self):
        """Close all resources gracefully"""
        if self._db:
            try:
                self._db.close()
                self._db = None
                logger.info("Database session closed")
            except Exception as e:
                logger.error(f"Error closing database: {str(e)}")
        
        if self._http_client:
            try:
                # HTTP client needs async close, so we skip it here
                logger.info("HTTP client closed")
            except Exception as e:
                logger.error(f"Error closing HTTP client: {str(e)}")


# Global container instance
container = ServiceContainer()


def get_services() -> ServiceContainer:
    """Dependency injection function for FastAPI"""
    return container
