"""
Session management module to avoid circular imports
"""
import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

# In-memory session storage (replace with Redis/database in production)
active_sessions: Dict[str, dict] = {}

def generate_session_id() -> str:
    """Generate a unique session ID"""
    return str(uuid.uuid4())

def hash_session_id(session_id: str) -> str:
    """Hash session ID for security"""
    return hashlib.sha256(session_id.encode()).hexdigest()[:16]

def create_session(username: str, is_admin: bool, display_name: str, remember_me: bool = False) -> tuple[str, Dict]:
    """Create a new session and return session_id and session_data"""
    session_id = generate_session_id()
    session_hash = hash_session_id(session_id)
    
    session_data = {
        "username": username,
        "is_admin": is_admin,
        "display_name": display_name,
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(hours=8),  # Default 8 hours
        "remember_me": remember_me
    }
    
    if remember_me:
        session_data["expires_at"] = datetime.now() + timedelta(days=30)  # 30 days for remember me
    
    active_sessions[session_hash] = session_data
    return session_id, session_data

def get_session(session_id: str) -> Optional[Dict]:
    """Get session by session ID"""
    if not session_id:
        return None
        
    session_hash = hash_session_id(session_id)
    session_data = active_sessions.get(session_hash)
    
    if not session_data:
        return None
        
    # Check if session has expired
    if session_data.get("expires_at") and datetime.now() > session_data["expires_at"]:
        # Session expired, remove it
        del active_sessions[session_hash]
        return None
        
    return session_data

def clear_session(session_id: str) -> bool:
    """Clear/delete a session"""
    if not session_id:
        return False
        
    session_hash = hash_session_id(session_id)
    if session_hash in active_sessions:
        username = active_sessions[session_hash].get("username", "unknown")
        del active_sessions[session_hash]
        logger.info(f"Session cleared for user: {username}")
        return True
    return False

def verify_session(session_data: Dict) -> bool:
    """Verify if session is valid and not expired"""
    if not session_data:
        return False
        
    # Check expiration
    expires_at = session_data.get("expires_at")
    if expires_at and datetime.now() > expires_at:
        return False
        
    return True

def extend_session(session_id: str, hours: int = 8) -> bool:
    """Extend session expiration time"""
    if not session_id:
        return False
        
    session_hash = hash_session_id(session_id)
    if session_hash in active_sessions:
        active_sessions[session_hash]["expires_at"] = datetime.now() + timedelta(hours=hours)
        return True
    return False

def cleanup_expired_sessions() -> int:
    """Clean up expired sessions and return count of cleaned sessions"""
    current_time = datetime.now()
    expired_sessions = []
    
    for session_hash, session_data in active_sessions.items():
        if session_data.get("expires_at") and current_time > session_data["expires_at"]:
            expired_sessions.append(session_hash)
    
    for session_hash in expired_sessions:
        username = active_sessions[session_hash].get("username", "unknown")
        del active_sessions[session_hash]
        logger.debug(f"Expired session cleaned for user: {username}")
    
    if expired_sessions:
        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
    
    return len(expired_sessions)

def get_active_sessions_count() -> int:
    """Get count of active sessions"""
    # Clean expired sessions first
    cleanup_expired_sessions()
    return len(active_sessions)

def get_session_info(session_id: str) -> Optional[Dict]:
    """Get session information by session ID"""
    session_data = get_session(session_id)
    
    if not verify_session(session_data):
        return None
    
    return {
        "username": session_data.get("username"),
        "display_name": session_data.get("display_name"),
        "is_admin": session_data.get("is_admin", False),
        "created_at": session_data.get("created_at"),
        "expires_at": session_data.get("expires_at")
    }

def is_session_valid(session_id: str) -> bool:
    """Check if a session ID is valid"""
    session_data = get_session(session_id)
    return verify_session(session_data)
