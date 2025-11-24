# Request/Response Logging Middleware

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import uuid
from core.logging import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log all HTTP requests and responses"""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Generate request ID for tracking
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Record request details
        start_time = time.time()
        method = request.method
        path = request.url.path
        
        logger.info(f"→ {method} {path}", extra={"request_id": request_id})
        
        try:
            response = await call_next(request)
            
            # Record response details
            duration = time.time() - start_time
            status_code = response.status_code
            
            logger.info(
                f"← {status_code} {method} {path} ({duration:.3f}s)",
                extra={"request_id": request_id, "status_code": status_code, "duration": duration}
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            return response
            
        except Exception as exc:
            duration = time.time() - start_time
            logger.error(
                f"✗ ERROR {method} {path} ({duration:.3f}s): {str(exc)}",
                extra={"request_id": request_id},
                exc_info=True
            )
            raise
