"""Admin authentication utilities."""

import secrets
from typing import Optional

from fastapi import Cookie, HTTPException, status
from fastapi.responses import RedirectResponse

from app.config import settings
from app.utils.logger import logger


# In-memory session storage (for MVP simplicity)
_sessions: dict[str, dict] = {}


def generate_session_id() -> str:
    """Generate a secure random session ID."""
    return secrets.token_urlsafe(32)


def create_session(username: str) -> str:
    """
    Create a new session for authenticated user.
    
    Args:
        username: The username of the authenticated user
    
    Returns:
        Session ID
    """
    session_id = generate_session_id()
    _sessions[session_id] = {
        'username': username,
        'authenticated': True
    }
    logger.info(f"Session created for user: {username}")
    return session_id


def get_session(session_id: str | None) -> dict | None:
    """
    Get session data by session ID.
    
    Args:
        session_id: The session ID from cookie
    
    Returns:
        Session data dict or None if not found
    """
    if not session_id:
        return None
    return _sessions.get(session_id)


def destroy_session(session_id: str | None) -> None:
    """
    Destroy a session.
    
    Args:
        session_id: The session ID to destroy
    """
    if session_id and session_id in _sessions:
        username = _sessions[session_id].get('username', 'unknown')
        del _sessions[session_id]
        logger.info(f"Session destroyed for user: {username}")


def verify_credentials(username: str, password: str) -> bool:
    """
    Verify admin credentials.
    
    Args:
        username: The username to verify
        password: The password to verify
    
    Returns:
        True if credentials are valid, False otherwise
    """
    return (
        username == settings.ADMIN_USERNAME and
        password == settings.ADMIN_PASSWORD
    )


# FastAPI dependency for authentication
async def get_current_session(session_id: Optional[str] = Cookie(None)) -> dict:
    """
    FastAPI dependency to verify authentication.
    
    Args:
        session_id: Session ID from cookie
    
    Returns:
        Session data dict
    
    Raises:
        HTTPException: If session is invalid, redirects to login
    """
    session = get_session(session_id)
    
    if not session or not session.get('authenticated'):
        logger.warning("Unauthorized access attempt")
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            headers={"Location": "/admin/login"}
        )
    
    return session
