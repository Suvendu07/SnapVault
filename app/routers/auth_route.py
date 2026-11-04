from fastapi import APIRouter, Depends, HTTPException, status,Response, BackgroundTasks, Cookie
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import UserRegister, UserResponse,LoginResponse,UserLogin, EmailRequest, VerifyEmailRequest, PasswordResetRequest
from app.core.config import settings
from app.core.dependencies import get_current_user
from app.services.acount_service import InvalidTokenError, create_verification_email, verify_email, create_password_reset_email, reset_password
from app.services.email_service import send_email
from app.services.auth_service import register_user, login_user, logout_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"],)




# REGISTER
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: UserRegister,
    db: Session = Depends(get_db),
):
    user, email_payload = register_user(
        db=db,
        full_name=data.full_name,
        email=data.email,
        password=data.password,
    )

    # Send the verification email using your existing email service.
    # Example: send_email(email_payload)

    return user


# LOGIN
@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
)
def login(
    data: UserLogin,
    response: Response,
    db: Session = Depends(get_db),
):
    user, raw_token = login_user(
        db=db,
        email=data.email,
        password=data.password,
    )

    response.set_cookie(
        key="session_token",
        value=raw_token,
        httponly=True,
        secure=False,  # Set True in production with HTTPS
        samesite="lax",
        max_age=60 * 60 * 24 * 7,
        path="/",
    )

    return {
        "message": "Login successful",
        "user": user,
    }


# LOGOUT
@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
)
def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    session_token: str | None = Cookie(
        default=None,
        alias="session_token",
    ),
):
    if not session_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session token is missing.",
        )

    logout_user(
        db=db,
        raw_token=session_token,
        user_id=current_user.id,
    )

    response.delete_cookie(
        key="session_token",
        path="/",
        httponly=True,
        secure=False,
        samesite="lax",
    )

    return {"message": "Logged out successfully"}


# GET CURRENT USER
@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user



# RESEND EMAIL VERIFICATION
@router.post("/resend-verification")
def resend_verification(
    data: EmailRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    email_payload = create_verification_email(
        db=db,
        email=str(data.email),
    )

    if email_payload is not None:
        background_tasks.add_task(
            send_email,
            **email_payload,
        )

    return {
        "message": (
            "If the account exists and needs verification, "
            "a verification email will be sent."
        )
    }


# VERIFY EMAIL
@router.post("/verify-email")
def verify_email_route(
    data: VerifyEmailRequest,
    db: Session = Depends(get_db),
):
    try:
        verify_email(
            db=db,
            raw_token=data.token,
        )

        return {
            "message": "Email verified successfully"
        }

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )


# FORGOT PASSWORD
@router.post("/forgot-password")
def forgot_password(
    data: EmailRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    email_payload = create_password_reset_email(
        db=db,
        email=str(data.email),
    )

    if email_payload is not None:
        background_tasks.add_task(
            send_email,
            **email_payload,
        )

    return {
        "message": (
            "If an account exists with this email, "
            "a password reset link will be sent."
        )
    }


# RESET PASSWORD
@router.post("/reset-password")
def reset_password_route(
    data: PasswordResetRequest,
    db: Session = Depends(get_db),
):
    try:
        reset_password(
            db=db,
            raw_token=data.token,
            new_password=data.new_password,
        )

        return {
            "message": "Password reset successfully"
        }

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token",
        )