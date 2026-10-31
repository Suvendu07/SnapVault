from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.services.auth import get_valid_session


def get_current_user(session_token : Annotated[str | None, Cookie(alias="session_token"),] = None, db : Session = Depends(get_db),) -> User:
    
    if not session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required", )
    
    user_session = get_valid_session(db = db, raw_token = session_token,)
    
    if user_session is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session",)
    
    user = db.get(User, user_session.user_id)
    
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="User accout is unavailble",)
    
    return user
