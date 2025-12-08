# Simple Mock Authentication API (No Database Required)

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
import jwt
import bcrypt

router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Mock user storage (in-memory)
MOCK_USERS = {}

# JWT Secret (use environment variable in production)
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Request/Response Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    email: str
    name: Optional[str]
    role: str = "user"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """
    Register new user (SQLite database storage)
    """
    try:
        import sqlite3
        import hashlib
        import os

        # Connect to database - use absolute path
        db_path = os.path.join(os.path.dirname(__file__), '..', 'chatbot.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (user_data.email,))
        if cursor.fetchone():
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Hash password
        password_hash = hashlib.sha256(user_data.password.encode()).hexdigest()

        # Create user
        username = user_data.name or user_data.email.split("@")[0]
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, full_name, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (username, user_data.email, password_hash, user_data.name, datetime.utcnow()))

        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Create access token
        access_token = create_access_token(data={"sub": user_data.email, "user_id": user_id})

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserInfo(
                id=user_id,
                email=user_data.email,
                name=username,
                role="user"
            )
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """
    Login user (SQLite database authentication)
    """
    try:
        import sqlite3
        import hashlib
        import os

        # Connect to database - use absolute path
        db_path = os.path.join(os.path.dirname(__file__), '..', 'chatbot.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get user
        cursor.execute("SELECT id, username, email, password_hash FROM users WHERE email = ?", (credentials.email,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        user_id, username, email, stored_hash = result

        # Verify password
        if hashlib.sha256(credentials.password.encode()).hexdigest() != stored_hash:
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Update last login
        cursor.execute("UPDATE users SET last_login = ? WHERE id = ?", (datetime.utcnow(), user_id))
        conn.commit()
        conn.close()

        # Create token
        access_token = create_access_token(data={"sub": email, "user_id": user_id})

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserInfo(
                id=user_id,
                email=email,
                name=username,
                role="user"
            )
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(token: str):
    """
    Get current user from token
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        
        if email is None or email not in MOCK_USERS:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        user = MOCK_USERS[email]
        return {
            "email": user["email"],
            "name": user["name"],
            "role": user["role"]
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


# Health check
@router.get("/health")
async def health_check():
    """Check auth service health"""
    return {
        "status": "healthy",
        "users_count": len(MOCK_USERS),
        "timestamp": datetime.utcnow().isoformat()
    }
