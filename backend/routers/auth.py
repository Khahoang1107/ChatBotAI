# API Router: Authentication

from fastapi import APIRouter, Depends, HTTPException, status
from schemas.models import UserCreate, UserResponse, TokenResponse
from services.user_service import UserService
from core.logging import logger

router = APIRouter(prefix="/api/auth", tags=["authentication"])


async def get_user_service() -> UserService:
    """Dependency for user service"""
    return UserService()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, user_service: UserService = Depends(get_user_service)):
    """
    Register new user
    
    Args:
        user_data: User registration data (email, name, password)
        
    Returns:
        Created user response
    """
    try:
        logger.info(f"User registration attempt: {user_data.email}")
        user = await user_service.create_user(user_data)
        logger.info(f"User registered successfully: {user_data.email}")
        return user
    except Exception as e:
        logger.error(f"Registration failed for {user_data.email}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(email: str, password: str, user_service: UserService = Depends(get_user_service)):
    """
    Authenticate user and return JWT token
    
    Args:
        email: User email
        password: User password
        
    Returns:
        JWT access token
    """
    try:
        logger.info(f"Login attempt: {email}")
        user = await user_service.authenticate_user(email, password)
        
        if not user:
            logger.warning(f"Failed login attempt: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create JWT token
        access_token = user_service.create_access_token(user.id)
        
        logger.info(f"User logged in successfully: {email}")
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=1800  # 30 minutes
        )
        
    except Exception as e:
        logger.error(f"Login failed for {email}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str, user_service: UserService = Depends(get_user_service)):
    """
    Refresh JWT token
    
    Args:
        refresh_token: Refresh token from previous login
        
    Returns:
        New access token
    """
    try:
        # In production, verify refresh token validity and expiration
        # For now, just issue new token if valid
        user_id = user_service.verify_token(refresh_token)
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        access_token = user_service.create_access_token(user_id)
        logger.info(f"Token refreshed for user: {user_id}")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=1800
        )
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/me", response_model=UserResponse)
async def get_current_user(token: str, user_service: UserService = Depends(get_user_service)):
    """
    Get current logged-in user info
    
    Args:
        token: JWT access token from Authorization header
        
    Returns:
        Current user data
    """
    try:
        user_id = user_service.verify_token(token)
        user = await user_service.get_user_by_id(user_id)
        return user
    except Exception as e:
        logger.error(f"Failed to get current user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
