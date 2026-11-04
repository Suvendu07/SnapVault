import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.models.user_session import UserSession
from app.models.user_token import UserToken
from app.services.security import hash_password




class InvalidTokenError(Exception):
    pass


def _hash_token(token : str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _invalidate_previous_tokens(db : Session, user_id, purpose : str) -> None:
    
    now = datetime.now(timezone.utc)
    
    previous_tokens = db.scalars(
        select(UserToken).where(UserToken.user_id == user_id, UserToken.purpose == purpose, UserToken.used_at.is_(None),)
    ).all()
    
    
    for previous_token in previous_tokens:
        previous_token.used_at = now
        

def _create_token(db : Session, user_id, purpose : str, expire_in_mintues : int,) -> str:
    
    _invalidate_previous_tokens(db, user_id, purpose,)
    
    raw_token = secrets.token_urlsafe(32)
    
    token_record = UserToken(user_id = user_id, token_hash = _hash_token(raw_token), purpose = purpose,
                             expire_at = (datetime.now(timezone.utc) + timedelta(minutes=expire_in_mintues)),)
    
    db.add(token_record)
    
    return raw_token


def create_verification_email(db : Session, email : str,) -> dict | None:
    
    user = db.scalar(select(User).where(User.email == email))
    
    if user is None or user.is_email_verified:
        return None
    
    token = _create_token(db = db, user_id=user.id, purpose="email_verification", expire_in_mintues=(settings.EMAIL_VERIFICATION_EXPIRE_MINUTES),)
    
    db.commit()
    
    verification_url = (f"{settings.FRONTEND_URL}/verify-email"
                        f"?token={token}")
    
    return {
        "recipient": user.email,
        "subject": "Verify your email address",
        "body": (
            f"Hello {user.full_name},\n\n"
            "Please verify your email address using this link:\n"
            f"{verification_url}\n\n"
            f"This link expires in "
            f"{settings.EMAIL_VERIFICATION_EXPIRE_MINUTES} minutes.\n\n"
            "If you did not request this, ignore this email."
        ),
    }
    
    
    
def verify_email(db : Session, raw_token : str,) -> User:
    
    token_record = db.scalar(select(UserToken).where(UserToken.token_hash == _hash_token(raw_token),
                                                     UserToken.purpose == "email_verification",
                                                     UserToken.used_at.is_(None),))
    
    now = datetime.now(timezone.utc)
    
    if token_record is None or token_record.expires_at <= now:
        raise InvalidTokenError(
            "Invalid or expired verification token"
        )

    user = db.get(User, token_record.user_id)

    if user is None:
        raise InvalidTokenError(
            "Invalid or expired verification token"
        )

    user.is_email_verified = True
    token_record.used_at = now

    db.commit()
    db.refresh(user)

    return user


def create_password_reset_email(
    db: Session,
    email: str,
) -> dict | None:

    user = db.scalar(
        select(User).where(User.email == email)
    )

    if user is None or not user.is_active:
        return None

    token = _create_token(
        db=db,
        user_id=user.id,
        purpose="password_reset",
        expires_in_minutes=(
            settings.PASSWORD_RESET_EXPIRE_MINUTES
        ),
    )

    db.commit()

    reset_url = (
        f"{settings.FRONTEND_URL}/reset-password"
        f"?token={token}"
    )

    return {
        "recipient": user.email,
        "subject": "Reset your password",
        "body": (
            f"Hello {user.full_name},\n\n"
            "Use this link to reset your password:\n"
            f"{reset_url}\n\n"
            f"This link expires in "
            f"{settings.PASSWORD_RESET_EXPIRE_MINUTES} minutes.\n\n"
            "If you did not request a password reset, "
            "ignore this email."
        ),
    }


def reset_password(
    db: Session,
    raw_token: str,
    new_password: str,
) -> None:

    now = datetime.now(timezone.utc)

    token_record = db.scalar(
        select(UserToken).where(
            UserToken.token_hash == _hash_token(raw_token),
            UserToken.purpose == "password_reset",
            UserToken.used_at.is_(None),
        )
    )

    if token_record is None or token_record.expires_at <= now:
        raise InvalidTokenError(
            "Invalid or expired password reset token"
        )

    user = db.get(User, token_record.user_id)

    if user is None or not user.is_active:
        raise InvalidTokenError(
            "Invalid or expired password reset token"
        )

    user.password_hash = hash_password(new_password)

    token_record.used_at = now

    # Revoke all existing sessions after a password reset.
    db.execute(
        update(UserSession)
        .where(
            UserSession.user_id == user.id,
            UserSession.revoked_at.is_(None),
        )
        .values(revoked_at=now)
    )

    db.commit()