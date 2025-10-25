"""
Authentication Service
Handles user registration, login, JWT tokens, and session management
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from models.user import User, UserSession, UserCreate, UserLogin, UserResponse, TokenResponse
from utils.database_tools import get_database_tools

class AuthService:
    """Authentication service for user management"""

    def __init__(self):
        self.db_tools = get_database_tools()
        self.jwt_secret = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")

    def register_user(self, user_data: UserCreate) -> UserResponse:
        """Register a new user"""
        conn = self.db_tools.connect()
        if not conn:
            raise Exception("Database connection failed")

        try:
            with conn.cursor() as cursor:
                # Check if user already exists
                cursor.execute(
                    "SELECT id FROM users WHERE username = %s OR email = %s",
                    (user_data.username, user_data.email)
                )
                if cursor.fetchone():
                    raise Exception("Username or email already exists")

                # Create new user
                user = User(
                    username=user_data.username,
                    email=user_data.email,
                    full_name=user_data.full_name
                )
                user.set_password(user_data.password)

                cursor.execute("""
                    INSERT INTO users (username, email, password_hash, full_name)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, username, email, full_name, is_active, is_admin, created_at
                """, (
                    user.username,
                    user.email,
                    user.password_hash,
                    user.full_name
                ))

                result = cursor.fetchone()
                conn.commit()

                return UserResponse(
                    id=result[0],
                    username=result[1],
                    email=result[2],
                    full_name=result[3],
                    is_active=result[4],
                    is_admin=result[5],
                    created_at=result[6],
                    last_login=None
                )

        except Exception as e:
            conn.rollback()
            raise e

    def authenticate_user(self, login_data: UserLogin) -> Optional[TokenResponse]:
        """Authenticate user and return token"""
        conn = self.db_tools.connect()
        if not conn:
            raise Exception("Database connection failed")

        try:
            with conn.cursor() as cursor:
                # Get user by username
                cursor.execute("""
                    SELECT id, username, email, password_hash, full_name, is_active, is_admin, created_at, last_login
                    FROM users WHERE username = %s
                """, (login_data.username,))

                result = cursor.fetchone()
                if not result:
                    return None

                user = User(
                    id=result[0],
                    username=result[1],
                    email=result[2],
                    password_hash=result[3],
                    full_name=result[4],
                    is_active=result[5],
                    is_admin=result[6],
                    created_at=result[7],
                    last_login=result[8]
                )

                # Verify password
                if not user.verify_password(login_data.password):
                    return None

                # Update last login
                cursor.execute(
                    "UPDATE users SET last_login = %s WHERE id = %s",
                    (datetime.utcnow(), user.id)
                )
                conn.commit()

                # Generate token
                token = user.generate_token()

                # Create user response
                user_response = UserResponse(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    full_name=user.full_name,
                    is_active=user.is_active,
                    is_admin=user.is_admin,
                    created_at=user.created_at,
                    last_login=user.last_login
                )

                return TokenResponse(
                    access_token=token,
                    user=user_response
                )

        except Exception as e:
            raise e

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        return User.verify_token(token)

    def get_current_user(self, token: str) -> Optional[UserResponse]:
        """Get current user from token"""
        payload = self.verify_token(token)
        if not payload:
            return None

        conn = self.db_tools.connect()
        if not conn:
            return None

        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, username, email, full_name, is_active, is_admin, created_at, last_login
                    FROM users WHERE id = %s
                """, (payload["user_id"],))

                result = cursor.fetchone()
                if not result:
                    return None

                return UserResponse(
                    id=result[0],
                    username=result[1],
                    email=result[2],
                    full_name=result[3],
                    is_active=result[4],
                    is_admin=result[5],
                    created_at=result[6],
                    last_login=result[7]
                )

        except Exception as e:
            return None

    def logout_user(self, token: str) -> bool:
        """Logout user by invalidating token"""
        # In a production system, you might want to add the token to a blacklist
        # For now, we'll just return success since JWT tokens are stateless
        return True

# Global auth service instance
auth_service = AuthService()