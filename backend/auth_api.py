from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from models.user import UserCreate, UserLogin, UserResponse, TokenResponse, UserRole
from utils.auth_utils import get_password_hash, verify_password, create_access_token, get_current_user, get_current_admin_user
from utils.logger import setup_logger
from utils.database_tools import get_database_tools


logger = setup_logger("auth_api")
db_tools = get_database_tools()

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    """Register new user"""
    try:
        if not db_tools:
            raise HTTPException(status_code=503, detail="Database unavailable")
        
        conn = db_tools.connect()
        if not conn:
            raise HTTPException(status_code=500, detail="DB connection failed")
        
        with conn.cursor() as cursor:
            username = user.username or user.email.split("@")[0]
            cursor.execute("SELECT id FROM users WHERE username = %s OR email = %s", (username, user.email))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="User exists")
            
            password_hash = get_password_hash(user.password)
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, full_name, role, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, username, email, full_name, role, is_active, created_at
            """, (username, user.email, password_hash, user.full_name, UserRole.USER.value, datetime.utcnow()))
            
            result = cursor.fetchone()
            conn.commit()
            
            return UserResponse(
                id=result["id"],
                username=result["username"],
                email=result["email"],
                full_name=result["full_name"],
                role=UserRole(result["role"]),
                is_active=result["is_active"],
                created_at=result["created_at"],
                last_login=None
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@auth_router.post("/login", response_model=TokenResponse)
async def login_user(user_credentials: UserLogin):
    """Login user"""
    try:
        if not db_tools:
            raise HTTPException(status_code=503, detail="Database unavailable")
        
        conn = db_tools.connect()
        if not conn:
            raise HTTPException(status_code=500, detail="DB connection failed")
        
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, username, email, password_hash, full_name, role, is_active, created_at, last_login
                FROM users WHERE email = %s
            """, (user_credentials.email,))
            
            result = cursor.fetchone()
            if not result or not verify_password(user_credentials.password, result["password_hash"]):
                raise HTTPException(status_code=401, detail="Invalid credentials")
            
            cursor.execute("UPDATE users SET last_login = %s WHERE id = %s", (datetime.utcnow(), result["id"]))
            conn.commit()
            
            access_token = create_access_token({
                "sub": result["email"],
                "user_id": result["id"],
                "username": result["username"],
                "role": result["role"]
            })
            
            user_response = UserResponse(
                id=result["id"],
                username=result["username"],
                email=result["email"],
                full_name=result["full_name"],
                role=UserRole(result["role"]),
                is_active=result["is_active"],
                created_at=result["created_at"],
                last_login=datetime.utcnow()
            )
            
            return TokenResponse(access_token=access_token, token_type="bearer", user=user_response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user_data=Depends(get_current_user)):
    """Get current user info"""
    try:
        if not db_tools:
            raise HTTPException(status_code=503, detail="Database unavailable")
        
        conn = db_tools.connect()
        if not conn:
            raise HTTPException(status_code=503, detail="DB connection failed")
        
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, username, email, full_name, role, is_active, created_at, last_login
                FROM users WHERE email = %s
            """, (current_user_data.username,))
            
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="User not found")
            
            return UserResponse(
                id=result["id"],
                username=result["username"],
                email=result["email"],
                full_name=result["full_name"],
                role=UserRole(result["role"]),
                is_active=result["is_active"],
                created_at=result["created_at"],
                last_login=result["last_login"]
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
