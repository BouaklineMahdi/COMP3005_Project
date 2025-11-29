# app/security.py

import secrets
from typing import Dict

from fastapi import Depends, Header, HTTPException, status
from pydantic import BaseModel, EmailStr


class SessionData(BaseModel):
    role: str     # "member" | "trainer" | "admin"
    user_id: int
    email: EmailStr


# In-memory session store: token -> SessionData
_SESSIONS: Dict[str, SessionData] = {}


def create_session(role: str, user_id: int, email: str) -> str:
    """
    Create a new session token for a logged-in user.
    """
    token = secrets.token_hex(32)
    _SESSIONS[token] = SessionData(role=role, user_id=user_id, email=email)
    return token


def get_current_session(
    authorization: str = Header(..., alias="Authorization"),
) -> SessionData:
    """
    Extract and validate the bearer token from Authorization header.
    Expect header: Authorization: Bearer <token>
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )
    token = authorization.split(" ", 1)[1].strip()
    session = _SESSIONS.get(token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return session


def require_role(expected_role: str):
    """
    Dependency factory that ensures the current session has the given role.
    Usage in endpoints:
        @router.get("/something")
        def handler(session: SessionData = Depends(require_role("admin"))):
            ...
    """
    def _dep(session: SessionData = Depends(get_current_session)) -> SessionData:
        if session.role != expected_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {expected_role} role",
            )
        return session

    return _dep
