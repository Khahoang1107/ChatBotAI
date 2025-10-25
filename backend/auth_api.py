"""
API Documentation cho Authentication System
===========================================

Swagger/OpenAPI documentation cho hệ thống xác thực của AI Invoice Assistant.

Endpoints chính:
- POST /auth/register - Đăng ký tài khoản mới
- POST /auth/login - Đăng nhập
- GET /auth/login - Đăng nhập (GET method for testing)
- GET /auth/me - Lấy thông tin user hiện tại
- POST /auth/logout - Đăng xuất

Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc
OpenAPI JSON: http://localhost:8000/openapi.json
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

# Import models và services
from models.user import User, UserCreate, UserLogin, UserResponse, TokenResponse
from utils.database_tools import get_database_tools

# Auth configuration
import os
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

from passlib.context import CryptContext
from jose import JWTError, jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Database tools
db_tools = get_database_tools()

# Auth utilities
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")  # Changed from username to email
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Use database tools directly
    conn = db_tools.connect()
    if not conn:
        raise credentials_exception

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, username, email, full_name, is_active, is_admin, created_at, last_login
                FROM users WHERE email = %s
            """, (email,))  # Changed from username to email
            result = cursor.fetchone()

            if not result:
                raise credentials_exception

            # Create user object from result
            user = User(
                id=result[0],
                username=result[1],
                email=result[2],
                password_hash="",  # Not needed for response
                full_name=result[3],
                is_active=result[4],
                is_admin=result[5],
                created_at=result[6],
                last_login=result[7]
            )
            return user

    except Exception as e:
        raise credentials_exception

# Tạo router cho auth endpoints
auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not found"},
        422: {"description": "Validation error"},
    },
)

@auth_router.post(
    "/register",
    response_model=UserResponse,
    summary="Đăng ký tài khoản mới",
    description="""
    Tạo tài khoản người dùng mới cho hệ thống AI Invoice Assistant.

    **Yêu cầu:**
    - Username phải là duy nhất
    - Email phải là duy nhất và có định dạng hợp lệ
    - Password phải có ít nhất 6 ký tự

    **Ví dụ request:**
    ```json
    {
        "username": "johndoe",
        "email": "john@example.com",
        "password": "securepassword123",
        "full_name": "John Doe"
    }
    ```
    """,
    response_description="Thông tin tài khoản vừa tạo"
)
async def register_user(user: UserCreate):
    """
    📝 Đăng ký user mới

    Tạo tài khoản mới với thông tin được cung cấp.
    """
    try:
        # Check if user already exists
        conn = db_tools.connect()
        if not conn:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection failed"
            )

        with conn.cursor() as cursor:
            # Generate username from email if not provided
            username = user.username
            if not username:
                # Create username from email (part before @)
                username = user.email.split('@')[0]
                # Ensure uniqueness by checking existing usernames
                base_username = username
                counter = 1
                while True:
                    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                    if not cursor.fetchone():
                        break
                    username = f"{base_username}{counter}"
                    counter += 1

            cursor.execute(
                "SELECT id FROM users WHERE username = %s OR email = %s",
                (username, user.email)
            )
            if cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username hoặc email đã tồn tại"
                )

            # Create new user
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            password_hash = pwd_context.hash(user.password)

            cursor.execute("""
                INSERT INTO users (username, email, password_hash, full_name, created_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, username, email, full_name, is_active, is_admin, created_at
            """, (
                username,
                user.email,
                password_hash,
                user.full_name,
                datetime.utcnow()
            ))

            result = cursor.fetchone()
            conn.commit()

            return UserResponse(
                id=result['id'],
                username=result['username'],
                email=result['email'],
                full_name=result['full_name'],
                is_active=result['is_active'],
                is_admin=result['is_admin'],
                created_at=result['created_at'],
                last_login=None
            )

    except HTTPException:
        raise
    except Exception as e:
        if 'conn' in locals() and conn:
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi server: {str(e)}"
        )

@auth_router.post(
    "/login",
    response_model=TokenResponse,
    summary="Đăng nhập tài khoản",
    description="""
    Đăng nhập vào hệ thống và nhận JWT token.

    **Yêu cầu:**
    - Email và password hợp lệ

    **Ví dụ request:**
    ```json
    {
        "email": "john@example.com",
        "password": "securepassword123"
    }
    ```

    **Ví dụ response:**
    ```json
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer",
        "user": {
            "id": 1,
            "username": "johndoe",
            "email": "john@example.com",
            "full_name": "John Doe",
            "is_active": true,
            "is_admin": false,
            "created_at": "2025-10-25T10:00:00Z",
            "last_login": "2025-10-25T10:30:00Z"
        }
    }
    ```
    """,
    response_description="JWT token và thông tin user"
)
async def login_user(user_credentials: UserLogin):
    """
    🔐 Đăng nhập user

    Xác thực thông tin đăng nhập và trả về JWT token.
    """
    try:
        conn = db_tools.connect()
        if not conn:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection failed"
            )

        with conn.cursor() as cursor:
            # Get user by email (changed from username)
            cursor.execute("""
                SELECT id, username, email, password_hash, full_name, is_active, is_admin, created_at, last_login
                FROM users WHERE email = %s
            """, (user_credentials.email,))  # Changed from user_credentials.username

            result = cursor.fetchone()
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Email hoặc mật khẩu không đúng",  # Changed from "Tên đăng nhập"
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Verify password
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            if not pwd_context.verify(user_credentials.password, result['password_hash']):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Email hoặc mật khẩu không đúng",  # Changed from "Tên đăng nhập"
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Update last login
            cursor.execute(
                "UPDATE users SET last_login = %s WHERE id = %s",
                (datetime.utcnow(), result['id'])
            )
            conn.commit()

            # Create access token
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": result['email']}, expires_delta=access_token_expires
            )

            user_response = UserResponse(
                id=result['id'],
                username=result['username'],
                email=result['email'],
                full_name=result['full_name'],
                is_active=result['is_active'],
                is_admin=result['is_admin'],
                created_at=result['created_at'],
                last_login=result['last_login']
            )

            return TokenResponse(
                access_token=access_token,
                token_type="bearer",
                user=user_response
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi server: {str(e)}"
        )

@auth_router.get(
    "/login",
    summary="Đăng nhập tài khoản (GET)",
    description="""
    Endpoint GET để test đăng nhập. Sử dụng query parameters thay vì JSON body.

    **Ví dụ:** `/auth/login?email=john@example.com&password=securepassword123`

    **Response:** JWT token và thông tin user (giống POST endpoint)
    """,
    response_description="JWT token và thông tin user"
)
async def login_user_get(email: str, password: str):
    """
    🔐 Đăng nhập user (GET method)

    Xác thực thông tin đăng nhập qua query parameters và trả về JWT token.
    """
    # Create UserLogin object from query params
    user_credentials = UserLogin(email=email, password=password)  # Changed from username=username

    # Use the same logic as POST endpoint
    try:
        conn = db_tools.connect()
        if not conn:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection failed"
            )

        with conn.cursor() as cursor:
            # Get user by email (changed from username)
            cursor.execute("""
                SELECT id, username, email, password_hash, full_name, is_active, is_admin, created_at, last_login
                FROM users WHERE email = %s
            """, (user_credentials.email,))  # Changed from user_credentials.username

            result = cursor.fetchone()
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Email hoặc mật khẩu không đúng",  # Changed from "Tên đăng nhập"
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Verify password
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            if not pwd_context.verify(user_credentials.password, result['password_hash']):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Email hoặc mật khẩu không đúng",  # Changed from "Tên đăng nhập"
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Update last login
            cursor.execute(
                "UPDATE users SET last_login = %s WHERE id = %s",
                (datetime.utcnow(), result['id'])
            )
            conn.commit()

            # Create access token
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": result['email']}, expires_delta=access_token_expires
            )

            user_response = UserResponse(
                id=result['id'],
                username=result['username'],
                email=result['email'],
                full_name=result['full_name'],
                is_active=result['is_active'],
                is_admin=result['is_admin'],
                created_at=result['created_at'],
                last_login=result['last_login']
            )

            return TokenResponse(
                access_token=access_token,
                token_type="bearer",
                user=user_response
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi server: {str(e)}"
        )

@auth_router.get(
    "/me",
    response_model=UserResponse,
    summary="Lấy thông tin user hiện tại",
    description="""
    Lấy thông tin của user đang đăng nhập dựa trên JWT token.

    **Yêu cầu:**
    - Phải có Authorization header với Bearer token

    **Header mẫu:**
    ```
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    ```
    """,
    response_description="Thông tin user hiện tại"
)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    👤 Lấy thông tin user hiện tại

    Trả về thông tin của user đang được xác thực.
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )

@auth_router.post(
    "/logout",
    summary="Đăng xuất",
    description="""
    Đăng xuất user (client-side token removal).

    **Lưu ý:** JWT tokens là stateless, endpoint này chỉ trả về success.
    Client cần xóa token khỏi storage.
    """,
    response_description="Thông báo đăng xuất thành công"
)
async def logout_user():
    """
    🚪 Đăng xuất

    Đăng xuất user khỏi hệ thống.
    """
    return {
        "message": "Đăng xuất thành công",
        "timestamp": datetime.utcnow().isoformat()
    }

@auth_router.get(
    "/verify-token",
    summary="Xác thực JWT token",
    description="""
    Kiểm tra tính hợp lệ của JWT token.

    **Yêu cầu:**
    - Token trong query parameter

    **Ví dụ:** `/auth/verify-token?token=eyJhbGciOiJIUzI1NiIs...`
    """,
    response_description="Kết quả xác thực token"
)
async def verify_token(token: str):
    """
    🔍 Xác thực JWT token

    Kiểm tra tính hợp lệ của token.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "valid": True,
            "user_id": payload.get("user_id"),
            "username": payload.get("username"),
            "expires_at": datetime.fromtimestamp(payload.get("exp")).isoformat(),
            "timestamp": datetime.utcnow().isoformat()
        }
    except JWTError as e:
        return {
            "valid": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Export router để import vào main.py
__all__ = ["auth_router"]