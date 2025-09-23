"""
Authentication utilities for JWT and password handling
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def generate_token(user_id: int, expires_delta: timedelta = None) -> str:
    """Generate a JWT token for a user"""
    if expires_delta is None:
        expires_delta = timedelta(hours=1)
    
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + expires_delta,
        'iat': datetime.utcnow()
    }
    
    return jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token"""
    try:
        payload = jwt.decode(
            token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError('Token has expired')
    except jwt.InvalidTokenError:
        raise ValueError('Invalid token')


def require_auth(f):
    """Decorator to require authentication for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Authentication required', 'message': str(e)}), 401
    
    return decorated_function


def require_admin(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            
            # Check if user is admin (you can implement your own logic)
            from models import User
            user = User.query.get(user_id)
            
            if not user or user.username != 'admin':  # Simple admin check
                return jsonify({'error': 'Admin privileges required'}), 403
            
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Authentication required', 'message': str(e)}), 401
    
    return decorated_function


def get_current_user():
    """Get the current authenticated user"""
    try:
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        from models import User
        return User.query.get(user_id)
    except:
        return None


def validate_password_strength(password: str) -> list:
    """Validate password strength and return list of issues"""
    issues = []
    
    if len(password) < 8:
        issues.append("Password must be at least 8 characters long")
    
    if not any(c.isupper() for c in password):
        issues.append("Password must contain at least one uppercase letter")
    
    if not any(c.islower() for c in password):
        issues.append("Password must contain at least one lowercase letter")
    
    if not any(c.isdigit() for c in password):
        issues.append("Password must contain at least one number")
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        issues.append("Password must contain at least one special character")
    
    return issues


def generate_api_key(user_id: int) -> str:
    """Generate an API key for a user"""
    import secrets
    import hashlib
    
    # Generate a random string
    random_string = secrets.token_urlsafe(32)
    
    # Include user ID and timestamp for uniqueness
    unique_string = f"{user_id}_{datetime.utcnow().isoformat()}_{random_string}"
    
    # Hash it to create the API key
    api_key = hashlib.sha256(unique_string.encode()).hexdigest()
    
    return f"iva_{api_key[:32]}"  # iva = Invoice App prefix


def validate_api_key(api_key: str) -> bool:
    """Validate an API key format"""
    if not api_key.startswith("iva_"):
        return False
    
    if len(api_key) != 36:  # iva_ + 32 characters
        return False
    
    # Check if the rest is valid hex
    try:
        int(api_key[4:], 16)
        return True
    except ValueError:
        return False


def rate_limit_key(user_id: int = None) -> str:
    """Generate a rate limiting key"""
    if user_id:
        return f"rate_limit:user:{user_id}"
    else:
        # Use IP address for anonymous requests
        return f"rate_limit:ip:{request.remote_addr}"


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input"""
    if not text:
        return ""
    
    # Remove potential XSS
    import re
    text = re.sub(r'<[^>]*>', '', text)  # Remove HTML tags
    text = text.replace('javascript:', '')
    text = text.replace('data:', '')
    
    # Limit length
    text = text[:max_length]
    
    # Strip whitespace
    return text.strip()


def validate_email(email: str) -> bool:
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def mask_sensitive_data(data: dict) -> dict:
    """Mask sensitive data in logs"""
    sensitive_keys = ['password', 'token', 'api_key', 'secret', 'key']
    masked_data = data.copy()
    
    for key, value in masked_data.items():
        if any(sensitive_key in key.lower() for sensitive_key in sensitive_keys):
            if isinstance(value, str) and len(value) > 4:
                masked_data[key] = f"{value[:2]}***{value[-2:]}"
            else:
                masked_data[key] = "***"
    
    return masked_data


def audit_log(action: str, user_id: int = None, details: dict = None):
    """Log audit events"""
    from datetime import datetime
    
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'action': action,
        'user_id': user_id,
        'ip_address': request.remote_addr if request else None,
        'user_agent': request.headers.get('User-Agent') if request else None,
        'details': mask_sensitive_data(details) if details else {}
    }
    
    # Log to application logger
    current_app.logger.info(f"AUDIT: {action} by user {user_id}", extra=log_entry)
    
    # Here you could also save to a dedicated audit log table in the database
    # or send to an external audit service