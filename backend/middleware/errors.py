# Error Handling Middleware

from fastapi import Request, status
from fastapi.responses import JSONResponse
from core.exceptions import APIException
from core.logging import logger
import uuid


async def api_exception_handler(request: Request, exc: APIException):
    """Handle custom API exceptions"""
    request_id = str(uuid.uuid4())
    
    logger.error(
        f"API Error [{request_id}] {exc.__class__.__name__}: {exc.message}",
        extra={"request_id": request_id, "path": request.url.path}
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "request_id": request_id
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    request_id = str(uuid.uuid4())
    
    logger.error(
        f"Unhandled Exception [{request_id}]: {str(exc)}",
        extra={"request_id": request_id, "path": request.url.path},
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "request_id": request_id
        }
    )
