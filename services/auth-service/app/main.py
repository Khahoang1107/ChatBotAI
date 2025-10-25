"""
🚀 Auth Service - Microservice for Authentication & User Management
==============================================================

Handles user authentication, registration, JWT token management, and user profiles.

Endpoints:
- POST /register - User registration
- POST /login - User login with JWT token
- GET /me - Get current user info
- POST /logout - User logout
- GET /health - Health check

Database: PostgreSQL with users and user_sessions tables
Port: 8001
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import logging
import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import local modules
from models.user import User, UserCreate, UserLogin, UserResponse, TokenResponse, UserSession
from utils.database import get_db, create_tables
from utils.auth import (
    authenticate_user, create_access_token, get_current_user,
    get_password_hash, verify_password, SECRET_KEY, ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Initialize FastAPI app
app = FastAPI(
    title="Auth Service",
    description="Authentication & User Management Microservice",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security scheme
security = HTTPBearer()

# ===================== HEALTH CHECK =====================

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "service": "auth-service",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

# ===================== AUTH ENDPOINTS =====================

@app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db=Depends(get_db)):
    """
    📝 Đăng ký user mới

    Body:
    {
        "username": "string",
        "email": "string",
        "password": "string",
        "full_name": "string (optional)"
    }
    """
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == user.username) | (User.email == user.email)
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )

        # Create new user
        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            password_hash=hashed_password,
            full_name=user.full_name
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        logger.info(f"✅ User registered: {user.username}")
        return UserResponse.from_orm(db_user)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error registering user: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.post("/login", response_model=TokenResponse)
def login_user(user_credentials: UserLogin, db=Depends(get_db)):
    """
    🔐 Đăng nhập user

    Body:
    {
        "username": "string",
        "password": "string"
    }

    Returns:
    {
        "access_token": "jwt_token",
        "token_type": "bearer",
        "user": {...}
    }
    """
    try:
        user = authenticate_user(db, user_credentials.username, user_credentials.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Update last login
        user.last_login = datetime.now()
        db.commit()

        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )

        # Create session record
        session_expires = datetime.now() + access_token_expires
        db_session = UserSession(
            user_id=user.id,
            session_token=access_token,
            expires_at=session_expires
        )
        db.add(db_session)
        db.commit()

        logger.info(f"✅ User logged in: {user.username}")
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.from_orm(user)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error logging in user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    👤 Lấy thông tin user hiện tại

    Headers:
    Authorization: Bearer <token>
    """
    return UserResponse.from_orm(current_user)

@app.post("/logout")
def logout_user(token: HTTPAuthorizationCredentials = Depends(security), db=Depends(get_db)):
    """
    🚪 Đăng xuất user

    Headers:
    Authorization: Bearer <token>

    Note: Removes session from database
    """
    try:
        # Remove session from database
        db.query(UserSession).filter(UserSession.session_token == token.credentials).delete()
        db.commit()

        logger.info("✅ User logged out")
        return {"message": "Successfully logged out"}

    except Exception as e:
        logger.error(f"❌ Error logging out: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.post("/verify-token")
def verify_token(token: HTTPAuthorizationCredentials = Depends(security), db=Depends(get_db)):
    """
    ✅ Xác thực JWT token

    Headers:
    Authorization: Bearer <token>

    Returns: User info if token is valid
    """
    try:
        # This will raise exception if token is invalid
        user = get_current_user(token, db)
        return {
            "valid": True,
            "user": UserResponse.from_orm(user)
        }
    except HTTPException:
        return {"valid": False, "user": None}

# ===================== STARTUP EVENT =====================

@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    try:
        create_tables()
        logger.info("✅ Auth service database initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise

# ===================== RUN SERVER =====================

if __name__ == "__main__":
    port = int(os.getenv("AUTH_SERVICE_PORT", "8001"))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )