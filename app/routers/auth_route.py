from fastapi import APIRouter, Depends, HTTPException, status,Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.user_session import UserSession
from app.schemas.auth import UserRegister, UserResponse,LoginResponse,UserLogin
from app.services.security import hash_password, verify_password
from app.services.auth import create_user_session, get_valid_session,hash_session_token
from app.core.config import settings
from app.core.dependencies import get_current_user


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



# LOGIN
@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK,)
def login_user(data: UserLogin, response : Response, db : Session = Depends(get_db)):
    
    user = db.scalar(select(User).where(User.email == str(data.email)))
    
    if user is None or not verify_password(data.password, user.password_hash,):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password",)
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Your account is inactive",)
    
    raw_token, _ = create_user_session(db = db, user_id=user.id,)
    
    try:
        db.commit()
        
    except Exception:
        db.rollback()
        raise

    
    response.set_cookie(key="session_token", value = raw_token, max_age=settings.SESSION_EXPIRE_MINUTES * 60,httponly=True, secure=settings.COOKIE_SECURE,samesite="lax",path="/",)
    
    return LoginResponse(
        message="Login successful", user = user,
    )
    
    
    
@router.post("/logout", status_code = status.HTTP_200_OK)
def logout_user(response : Response, current_user : User = Depends(get_current_user), db : Session = Depends(get_db), session_token : str = Depends(lambda : None),):
    
    return {
        "message" : "logout endpoint configuration pending"
    }
    
    
@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user