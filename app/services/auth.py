import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user_session import UserSession



def generate_session_token() -> str:
    return secrets.token_urlsafe(32)


def hash_session_token(token: str) -> str:
    
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()
    
    
    
    
def create_user_session(db : Session, user_id,) -> tuple[str, UserSession]:
    
    raw_token = generate_session_token()
    
    token_hash = hash_session_token(raw_token)
    
    expire_at = (datetime.now(timezone.utc) + timedelta(minutes=settings.SESSION_EXPIRE_MINUTES))
    
    user_session = UserSession(user_id = user_id, token_hash = token_hash, expire_at = expire_at,)
    
    db.add(user_session)
    db.flush()
    
    return raw_token, user_session


def get_valid_session(db : Session, raw_token : str,) -> UserSession | None:
    
    token_hash = hash_session_token(raw_token)
    
    statement = select(UserSession).where(UserSession.token_hash == token_hash,UserSession.revoke_at.is_(None), UserSession.expire_at > datetime.now(timezone.utc),)
    
    return db.scalar(statement)