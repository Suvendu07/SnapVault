from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.services.auth import get_valid_session
from app.services.auth_service import get_authenticated_user


def get_current_user(
    session_token: Annotated[
        str | None,
        Cookie(alias="session_token")
    ] = None,
    db: Session = Depends(get_db),
) -> User:

    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    user_session = get_valid_session(
        db=db,
        raw_token=session_token,
    )

    if user_session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )

    user = get_authenticated_user(
        db=db,
        user_id=user_session.user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is unavailable",
        )

    return user


def get_current_photographer(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:

    if current_user.role != "photographer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Photographer access required",
        )

    return current_user


def get_current_admin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:

    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return current_user