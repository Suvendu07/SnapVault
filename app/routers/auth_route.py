from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import UserRegister, UserResponse
from app.services.security import hash_password

router = APIRouter(prefix="/api/auth", tags=["Authentication"],)




@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED,)
def register_user(user : UserRegister, db : Session = Depends(get_db),) -> UserResponse:
    
    existing_user = db.scalar(select(User.id).where(User.email == str(user.email)))
    
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists",)
    
    hashed_password = hash_password(user.password)
    
    users = User(
        full_name=user.full_name,
        email=str(user.email),
        password_hash=hashed_password,
        role="photographer",
        is_email_verified=False,
        is_active=True,
    )

    # 4. Save the new user.
    try:
        db.add(users)
        db.commit()
        db.refresh(users)

    except IntegrityError:
        db.rollback()

        # Handles concurrent requests that try to register
        # the same email after the initial existence check.
        existing_user = db.scalar(
            select(User.id).where(User.email == str(user.email))
        )

        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists",
            )

        # Unexpected database constraint violation.
        raise

    # 5. FastAPI returns only fields declared in UserResponse.
    return users