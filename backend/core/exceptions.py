# Centralized Exception Handling

from fastapi import HTTPException, status
from typing import Any, Dict


class APIException(Exception):
    """Base API Exception"""
    def __init__(
        self, 
        message: str, 
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: Dict[str, Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail or {"error": message}
        super().__init__(self.message)


class AuthenticationException(APIException):
    """Authentication related errors"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class AuthorizationException(APIException):
    """Authorization related errors"""
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class ValidationException(APIException):
    """Validation errors"""
    def __init__(self, message: str = "Validation failed", errors: Dict = None):
        detail = {"error": message}
        if errors:
            detail["errors"] = errors
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, detail)


class ResourceNotFoundException(APIException):
    """Resource not found"""
    def __init__(self, resource: str, resource_id: Any = None):
        message = f"{resource} not found"
        if resource_id:
            message += f" (ID: {resource_id})"
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class DatabaseException(APIException):
    """Database operation errors"""
    def __init__(self, message: str = "Database error"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExternalServiceException(APIException):
    """External service (Groq, Google AI) errors"""
    def __init__(self, service: str, message: str):
        super().__init__(
            f"{service} error: {message}",
            status.HTTP_503_SERVICE_UNAVAILABLE
        )


class RateLimitException(APIException):
    """Rate limit exceeded"""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status.HTTP_429_TOO_MANY_REQUESTS)
