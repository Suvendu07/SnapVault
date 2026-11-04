from fastapi import HTTPException, status
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.user_session import UserSession
from app.services.acount_service import create_token
from app.services.auth import create_user_session, get_valid_session
from app.services.security import hash_password, verify_password

from app.core.config import settings


def register_user(
    db: Session,
    full_name: str,
    email: str,
    password: str,
) -> tuple[User, dict]:

    normalized_email = email.strip().lower()

    existing_user = db.scalar(
        select(User.id).where(User.email == normalized_email)
    )

    if existing_user is not None:
     raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="An account with this email already exists."
    )

    user = User(
        full_name=full_name.strip(),
        email=normalized_email,
        password_hash=hash_password(password),
        role="photographer",
        is_email_verified=False,
        is_active=True,
    )

    try:
        db.add(user)
        db.flush()

        token = create_token(
            db=db,
            user_id=user.id,
            purpose="email_verification",
            expires_in_minutes=(
                settings.EMAIL_VERIFICATION_EXPIRE_MINUTES
            ),
        )

        db.commit()
        db.refresh(user)

    except IntegrityError:
        db.rollback()

    raise HTTPException(
     status_code=status.HTTP_409_CONFLICT,
     detail="An account with this email already exists."
)

    verification_url = (
        f"{settings.FRONTEND_URL}/verify-email?token={token}"
    )

    email_payload = {
        "recipient": user.email,
        "subject": "Verify your email address",
        "body": (
            f"Hello {user.full_name},\n\n"
            "Please verify your email using this link:\n"
            f"{verification_url}\n\n"
            f"This link expires in "
            f"{settings.EMAIL_VERIFICATION_EXPIRE_MINUTES} minutes."
        ),
    }

    return user, email_payload

def login_user(
    db: Session,
    email: str,
    password: str,
) -> tuple[User, str]:

    normalized_email = email.strip().lower()

    user = db.scalar(
        select(User).where(User.email == normalized_email)
    )

    if user is None:
     raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password"
    )

    if not verify_password(password, user.password_hash):
     raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password"
    )

    if not user.is_active:
     raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Your account is inactive"
    )

    if not user.is_email_verified:
     raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Please verify your email before logging in"
    )
    raw_token, _ = create_user_session(
        db=db,
        user_id=user.id,
    )

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return user, raw_token


def logout_user(
    db: Session,
    raw_token: str,
    user_id,
) -> None:

    user_session = get_valid_session(
        db=db,
        raw_token=raw_token,
    )

    if user_session is None or user_session.user_id != user_id:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired session."
    )

    user_session.revoked_at = datetime.now(timezone.utc)

    db.commit()


def get_authenticated_user(
    db: Session,
    user_id,
) -> User | None:

    user = db.get(User, user_id)

    if user is None or not user.is_active:
        return None

    return user