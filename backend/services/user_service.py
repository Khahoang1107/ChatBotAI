# Service Layer: User Management

from typing import Optional
from datetime import datetime, timedelta
import jwt
from core.exceptions import (
    AuthenticationException,
    ValidationException,
    ResourceNotFoundException,
    DatabaseException
)
from core.dependencies import container
from schemas.models import UserCreate, UserResponse
from models.user import User


class UserService:
    """User management and authentication service"""
    
    def __init__(self):
        self.db = container.db
        self.settings = container.settings
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create new user with hashed password"""
        try:
            # Check if user exists
            existing = self.db.query(User).filter(User.email == user_data.email).first()
            if existing:
                raise ValidationException(f"User {user_data.email} already exists")
            
            # Hash password (using bcrypt in production)
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            hashed_password = pwd_context.hash(user_data.password)
            
            user = User(
                email=user_data.email,
                name=user_data.name,
                hashed_password=hashed_password,
                is_active=True,
                created_at=datetime.utcnow()
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                created_at=user.created_at,
                is_active=user.is_active
            )
        except ValidationException:
            raise
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(f"Failed to create user: {str(e)}")
    
    async def authenticate_user(self, email: str, password: str) -> Optional[UserResponse]:
        """Authenticate user by email and password"""
        try:
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            user = self.db.query(User).filter(User.email == email).first()
            if not user:
                raise AuthenticationException("Invalid email or password")
            
            if not pwd_context.verify(password, user.hashed_password):
                raise AuthenticationException("Invalid email or password")
            
            if not user.is_active:
                raise AuthenticationException("User account is disabled")
            
            return UserResponse.from_orm(user)
        except AuthenticationException:
            raise
        except Exception as e:
            raise DatabaseException(f"Authentication failed: {str(e)}")
    
    async def get_user_by_id(self, user_id: int) -> UserResponse:
        """Retrieve user by ID"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ResourceNotFoundException(f"User {user_id} not found")
            return UserResponse.from_orm(user)
        except ResourceNotFoundException:
            raise
        except Exception as e:
            raise DatabaseException(f"Failed to retrieve user: {str(e)}")
    
    def create_access_token(self, user_id: int, expires_delta: Optional[timedelta] = None) -> str:
        """Generate JWT access token"""
        if expires_delta is None:
            expires_delta = timedelta(minutes=30)
        
        expire = datetime.utcnow() + expires_delta
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(
            payload,
            self.settings.SECRET_KEY,
            algorithm="HS256"
        )
        return token
    
    def verify_token(self, token: str) -> int:
        """Verify JWT token and return user_id"""
        try:
            payload = jwt.decode(
                token,
                self.settings.SECRET_KEY,
                algorithms=["HS256"]
            )
            user_id = int(payload.get("sub"))
            return user_id
        except jwt.ExpiredSignatureError:
            raise AuthenticationException("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationException("Invalid token")
