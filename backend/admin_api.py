"""
Admin API endpoints for user management
========================================

Endpoints for admin users to manage other users in the system.

Endpoints:
- GET /admin/users - Get all users (admin only)
- PUT /admin/users/{user_id}/toggle-admin - Toggle admin status
- PUT /admin/users/{user_id}/toggle-active - Toggle user active status
- DELETE /admin/users/{user_id} - Delete user (admin only)
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
from datetime import datetime

# Import models và services
from models.user import User, UserResponse
from utils.database_tools import get_database_tools

# Import auth utilities
from auth_api import get_current_user

# Database tools
db_tools = get_database_tools()

# Tạo router cho admin endpoints
admin_router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - Admin access required"},
        404: {"description": "Not found"},
        422: {"description": "Validation error"},
    },
)

def require_admin(current_user: User = Depends(get_current_user)):
    """Dependency to ensure user is admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

@admin_router.get(
    "/users",
    response_model=List[UserResponse],
    summary="Get all users",
    description="""
    Retrieve a list of all users in the system.

    **Requirements:**
    - Admin privileges required
    - Returns all user information except passwords

    **Response:** List of user objects with full details
    """,
    response_description="List of all users"
)
async def get_all_users(admin_user: User = Depends(require_admin)):
    """
    👥 Get all users (Admin only)

    Returns a complete list of all users in the system.
    """
    try:
        conn = db_tools.connect()
        if not conn:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection failed"
            )

        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, username, email, full_name, is_active, is_admin, created_at, last_login
                FROM users
                ORDER BY created_at DESC
            """)

            results = cursor.fetchall()

            users = []
            for result in results:
                users.append(UserResponse(
                    id=result['id'],
                    username=result['username'],
                    email=result['email'],
                    full_name=result['full_name'],
                    is_active=result['is_active'],
                    is_admin=result['is_admin'],
                    created_at=result['created_at'],
                    last_login=result['last_login']
                ))

            return users

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@admin_router.put(
    "/users/{user_id}/toggle-admin",
    response_model=UserResponse,
    summary="Toggle admin status",
    description="""
    Toggle the admin status of a user.

    **Requirements:**
    - Admin privileges required
    - Cannot remove admin status from yourself

    **Parameters:**
    - user_id: ID of the user to modify

    **Response:** Updated user information
    """,
    response_description="Updated user information"
)
async def toggle_admin_status(
    user_id: int,
    admin_user: User = Depends(require_admin)
):
    """
    👑 Toggle admin status (Admin only)

    Grant or revoke admin privileges for a user.
    """
    try:
        # Prevent admin from removing their own admin status
        if user_id == admin_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot modify your own admin status"
            )

        conn = db_tools.connect()
        if not conn:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection failed"
            )

        with conn.cursor() as cursor:
            # Check if user exists
            cursor.execute("""
                SELECT id, username, email, full_name, is_active, is_admin, created_at, last_login
                FROM users WHERE id = %s
            """, (user_id,))

            result = cursor.fetchone()
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            # Toggle admin status
            new_admin_status = not result['is_admin']

            cursor.execute("""
                UPDATE users SET is_admin = %s WHERE id = %s
                RETURNING id, username, email, full_name, is_active, is_admin, created_at, last_login
            """, (new_admin_status, user_id))

            updated_result = cursor.fetchone()
            conn.commit()

            return UserResponse(
                id=updated_result['id'],
                username=updated_result['username'],
                email=updated_result['email'],
                full_name=updated_result['full_name'],
                is_active=updated_result['is_active'],
                is_admin=updated_result['is_admin'],
                created_at=updated_result['created_at'],
                last_login=updated_result['last_login']
            )

    except HTTPException:
        raise
    except Exception as e:
        if 'conn' in locals() and conn:
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@admin_router.put(
    "/users/{user_id}/toggle-active",
    response_model=UserResponse,
    summary="Toggle user active status",
    description="""
    Activate or deactivate a user account.

    **Requirements:**
    - Admin privileges required
    - Cannot deactivate your own account

    **Parameters:**
    - user_id: ID of the user to modify

    **Response:** Updated user information
    """,
    response_description="Updated user information"
)
async def toggle_user_active_status(
    user_id: int,
    admin_user: User = Depends(require_admin)
):
    """
    🚫 Toggle user active status (Admin only)

    Activate or deactivate a user account.
    """
    try:
        # Prevent admin from deactivating their own account
        if user_id == admin_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate your own account"
            )

        conn = db_tools.connect()
        if not conn:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection failed"
            )

        with conn.cursor() as cursor:
            # Check if user exists
            cursor.execute("""
                SELECT id, username, email, full_name, is_active, is_admin, created_at, last_login
                FROM users WHERE id = %s
            """, (user_id,))

            result = cursor.fetchone()
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            # Toggle active status
            new_active_status = not result['is_active']

            cursor.execute("""
                UPDATE users SET is_active = %s WHERE id = %s
                RETURNING id, username, email, full_name, is_active, is_admin, created_at, last_login
            """, (new_active_status, user_id))

            updated_result = cursor.fetchone()
            conn.commit()

            return UserResponse(
                id=updated_result['id'],
                username=updated_result['username'],
                email=updated_result['email'],
                full_name=updated_result['full_name'],
                is_active=updated_result['is_active'],
                is_admin=updated_result['is_admin'],
                created_at=updated_result['created_at'],
                last_login=updated_result['last_login']
            )

    except HTTPException:
        raise
    except Exception as e:
        if 'conn' in locals() and conn:
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@admin_router.delete(
    "/users/{user_id}",
    summary="Delete user",
    description="""
    Permanently delete a user account.

    **Requirements:**
    - Admin privileges required
    - Cannot delete your own account
    - Cannot delete other admin accounts

    **Parameters:**
    - user_id: ID of the user to delete

    **Response:** Success message
    """,
    response_description="Success message"
)
async def delete_user(
    user_id: int,
    admin_user: User = Depends(require_admin)
):
    """
    🗑️ Delete user (Admin only)

    Permanently remove a user account from the system.
    """
    try:
        # Prevent admin from deleting their own account
        if user_id == admin_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )

        conn = db_tools.connect()
        if not conn:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection failed"
            )

        with conn.cursor() as cursor:
            # Check if user exists and is not admin
            cursor.execute("""
                SELECT id, username, email, is_admin FROM users WHERE id = %s
            """, (user_id,))

            result = cursor.fetchone()
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            # Prevent deleting other admin accounts
            if result['is_admin']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot delete admin accounts"
                )

            # Delete the user
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()

            return {
                "message": f"User {result['username']} ({result['email']}) has been deleted successfully",
                "deleted_user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }

    except HTTPException:
        raise
    except Exception as e:
        if 'conn' in locals() and conn:
            conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

# Export router để import vào main.py
__all__ = ["admin_router"]</content>
<parameter name="filePath">F:\DoAnCN\backend\admin_api.py