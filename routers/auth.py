from fastapi import APIRouter, HTTPException, Depends, Request, Response
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

from models import LoginRequest, LoginResponse, SessionInfo, APIResponse
from database import DatabaseManager
from session_manager import (
    create_session, get_session, clear_session, hash_session_id,
    cleanup_expired_sessions, get_active_sessions_count, active_sessions
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, response: Response):
    """Admin login endpoint"""
    try:
        db_manager = DatabaseManager()
        
        # Validate credentials
        if db_manager.validate_admin_credentials(request.username, request.password):
            user_info = db_manager.get_user_info(request.username)
            
            # Create session using session manager
            session_id, session_data = create_session(
                username=request.username,
                is_admin=True,
                display_name=user_info.get("display_name", "Administrator"),
                remember_me=request.remember_me
            )
            
            session_hash = hash_session_id(session_id)
            
            # Set secure session cookie
            response.set_cookie(
                key="session_id",
                value=session_id,
                httponly=True,
                secure=False,  # Set to True in production with HTTPS
                samesite="lax",
                max_age=30*24*60*60 if request.remember_me else 8*60*60  # 30 days or 8 hours
            )
            
            logger.info(f"Successful login for user: {request.username}")
            
            return LoginResponse(
                success=True,
                message="Login successful",
                user_info={
                    "username": request.username,
                    "display_name": session_data["display_name"],
                    "is_admin": True
                },
                session_id=session_hash
            )
        else:
            logger.warning(f"Failed login attempt for user: {request.username}")
            return LoginResponse(
                success=False,
                message="Invalid username or password"
            )
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during login")

@router.post("/logout", response_model=APIResponse)
async def logout(request: Request, response: Response):
    """Logout endpoint"""
    try:
        session_id = request.cookies.get("session_id")
        
        if session_id:
            clear_session(session_id)
        
        # Clear session cookie
        response.delete_cookie(key="session_id")
        
        return APIResponse(
            success=True,
            message="Logged out successfully"
        )
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return APIResponse(
            success=False,
            message="Error during logout"
        )

@router.get("/session", response_model=SessionInfo)
async def get_session_info(request: Request):
    """Get current session information"""
    try:
        session_id = request.cookies.get("session_id")
        
        if not session_id:
            return SessionInfo(
                is_authenticated=False,
                is_admin=False
            )
        
        session_data = get_session(session_id)
        
        if not session_data:
            return SessionInfo(
                is_authenticated=False,
                is_admin=False
            )
        
        session_hash = hash_session_id(session_id)
        
        return SessionInfo(
            is_authenticated=True,
            is_admin=session_data.get("is_admin", False),
            username=session_data.get("username"),
            display_name=session_data.get("display_name"),
            session_id=session_hash
        )
        
    except Exception as e:
        logger.error(f"Session info error: {e}")
        return SessionInfo(
            is_authenticated=False,
            is_admin=False
        )

@router.post("/validate", response_model=APIResponse)
async def validate_session(request: Request):
    """Validate current session"""
    try:
        session_info = await get_session_info(request)
        
        if session_info.is_authenticated:
            return APIResponse(
                success=True,
                message="Session is valid",
                data={
                    "username": session_info.username,
                    "display_name": session_info.display_name,
                    "is_admin": session_info.is_admin
                }
            )
        else:
            return APIResponse(
                success=False,
                message="Session is invalid or expired"
            )
            
    except Exception as e:
        logger.error(f"Session validation error: {e}")
        return APIResponse(
            success=False,
            message="Error validating session"
        )

@router.delete("/cleanup-sessions")
async def cleanup_expired_sessions_endpoint():
    """Cleanup expired sessions (admin endpoint)"""
    try:
        cleaned_count = cleanup_expired_sessions()
        
        return APIResponse(
            success=True,
            message=f"Cleaned up {cleaned_count} expired sessions",
            data={"cleaned_sessions": cleaned_count}
        )
        
    except Exception as e:
        logger.error(f"Session cleanup error: {e}")
        return APIResponse(
            success=False,
            message="Error during session cleanup"
        )

@router.get("/active-sessions")
async def get_active_sessions(request: Request):
    """Get active sessions count (admin only)"""
    try:
        # Verify admin session
        session_info = await get_session_info(request)
        if not session_info.is_admin:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        active_count = get_active_sessions_count()
        
        return APIResponse(
            success=True,
            message=f"Currently {active_count} active sessions",
            data={
                "active_sessions": active_count,
                "timestamp": datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Active sessions error: {e}")
        return APIResponse(
            success=False,
            message="Error retrieving active sessions"
        )
