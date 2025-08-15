from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from session_manager import get_session, hash_session_id

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

async def get_current_session(request: Request) -> Optional[Dict[str, Any]]:
    """Get current session data from request"""
    try:
        session_id = request.cookies.get("session_id")
        
        if not session_id:
            return None
            
        return get_session(session_id)
        
    except Exception as e:
        logger.error(f"Error getting session: {e}")
        return None

async def get_current_user(request: Request) -> Optional[Dict[str, Any]]:
    """Get current authenticated user"""
    session_data = await get_current_session(request)
    
    if not session_data:
        return None
        
    return {
        "username": session_data.get("username"),
        "display_name": session_data.get("display_name"),
        "is_admin": session_data.get("is_admin", False),
        "session_id": hash_session_id(request.cookies.get("session_id", ""))
    }

async def require_auth(request: Request) -> Dict[str, Any]:
    """Require authentication - raises HTTPException if not authenticated"""
    user = await get_current_user(request)
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )
    
    return user

async def require_admin(request: Request) -> Dict[str, Any]:
    """Require admin authentication - raises HTTPException if not admin"""
    user = await require_auth(request)
    
    if not user.get("is_admin", False):
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    
    return user

async def optional_auth(request: Request) -> Optional[Dict[str, Any]]:
    """Optional authentication - returns user if authenticated, None if not"""
    return await get_current_user(request)

def verify_session(session_data: Dict[str, Any]) -> bool:
    """Verify if session is valid and not expired"""
    if not session_data:
        return False
        
    # Check expiration
    expires_at = session_data.get("expires_at")
    if expires_at and datetime.now() > expires_at:
        return False
        
    return True

# Dependency functions for FastAPI
def get_optional_user(request: Request):
    """FastAPI dependency for optional user"""
    return Depends(lambda: optional_auth(request))

def get_authenticated_user(request: Request):
    """FastAPI dependency for required authentication"""
    return Depends(lambda: require_auth(request))

def get_admin_user(request: Request):
    """FastAPI dependency for required admin authentication"""
    return Depends(lambda: require_admin(request))

class AuthenticationMiddleware:
    """Custom authentication middleware class"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Add user information to request state
            user = await get_current_user(request)
            request.state.user = user
            request.state.is_authenticated = user is not None
            request.state.is_admin = user.get("is_admin", False) if user else False
        
        await self.app(scope, receive, send)

# Error handlers
class AuthenticationError(Exception):
    """Custom authentication error"""
    def __init__(self, message: str, status_code: int = 401):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class AuthorizationError(Exception):
    """Custom authorization error"""
    def __init__(self, message: str, status_code: int = 403):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)
