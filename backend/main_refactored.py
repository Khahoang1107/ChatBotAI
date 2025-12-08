"""
🚀 FastAPI Backend - Refactored with Clean Architecture

Enterprise-grade FastAPI application with:
- Service layer architecture
- Dependency injection container
- Exception handling middleware
- Structured logging
- Modular routers
- Type validation with Pydantic

Run: uvicorn main:app --reload --port 8000
Or:  python main.py
"""

import sys
from pathlib import Path
from contextlib import asynccontextmanager
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Core imports
from config.settings import settings
from core.logging import logger
from core.dependencies import container
from core.exceptions import APIException

# Middleware imports
from middleware.logging import LoggingMiddleware
from middleware.errors import api_exception_handler, general_exception_handler

# Router imports
from routers import auth, chat, upload

# Legacy imports (backward compatibility)
try:
    from auth_api import router as auth_api_router
except ImportError:
    auth_api_router = None

try:
    from admin_api import router as admin_api_router
except ImportError:
    admin_api_router = None


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage app lifecycle
    
    Startup: Initialize services
    Shutdown: Clean up resources
    """
    # Startup
    logger.info("🚀 Application starting...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Database: {settings.DATABASE_URL}")
    
    try:
        # Create database tables
        from models.user import Base
        from models.chat import ChatHistory, UserSession
        engine = container.engine
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created")
    except Exception as e:
        logger.warning(f"⚠️ Could not create tables: {str(e)}")
    
    try:
        # Test database connection
        _ = container.db
        logger.info("✅ Database connection established")
    except Exception as e:
        logger.warning(f"⚠️ Database connection failed: {str(e)}")
    
    try:
        # Test Groq client
        groq = container.groq_client
        if groq:
            logger.info("✅ Groq AI client initialized")
        else:
            logger.warning("⚠️ Groq API key not configured")
    except Exception as e:
        logger.warning(f"⚠️ Groq client initialization failed: {str(e)}")
    
    logger.info("✅ Application ready to handle requests")
    
    yield  # App runs here
    
    # Shutdown
    logger.info("🛑 Application shutting down...")
    container.close()
    logger.info("✅ Resources cleaned up")


# Create FastAPI app with lifespan
app = FastAPI(
    title="ChatBotAI API",
    description="Enterprise chat and OCR backend",
    version="2.0.0",
    lifespan=lifespan
)

# Middleware configuration
logger.info("Configuring middleware...")

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

logger.info("✅ Middleware configured")

# Exception handlers
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

logger.info("✅ Exception handlers registered")


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """API root endpoint"""
    return {
        "message": "ChatBotAI API v2.0",
        "status": "running",
        "version": "2.0.0",
        "docs": "/docs",
        "environment": settings.ENVIRONMENT
    }


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {}
    }
    
    # Check database
    try:
        db = container.db
        health_status["services"]["database"] = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        health_status["services"]["database"] = "disconnected"
    
    # Check Groq
    try:
        groq = container.groq_client
        health_status["services"]["groq"] = "available" if groq else "not_configured"
    except Exception as e:
        logger.error(f"Groq health check failed: {str(e)}")
        health_status["services"]["groq"] = "unavailable"
    
    # Return degraded service if critical services down
    if health_status["services"].get("database") == "disconnected":
        health_status["status"] = "degraded"
        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=health_status)
    
    return health_status


# Register routers (new architecture)
logger.info("Registering API routers...")

# New modular routers - routers already have /api/auth, /api/chat, etc. in their prefix
try:
    app.include_router(auth.router)
    logger.info("✅ Auth router registered")
except Exception as e:
    logger.error(f"❌ Failed to register auth router: {e}")

try:
    app.include_router(chat.router)
    logger.info("✅ Chat router registered")
except Exception as e:
    logger.error(f"❌ Failed to register chat router: {e}")

try:
    app.include_router(upload.router)
    logger.info("✅ Upload router registered")
except Exception as e:
    logger.error(f"❌ Failed to register upload router: {e}")

logger.info("✅ API routers registration completed")


# Startup event (alternative to lifespan)
@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("Startup event triggered")


# Shutdown event (alternative to lifespan)
@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("Shutdown event triggered")


# Run application
if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on http://0.0.0.0:{settings.PORT}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
