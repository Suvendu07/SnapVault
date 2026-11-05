from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_photographer
from app.db.session import get_db
from app.models.user import User
from app.schemas.photographer import PhotographerProfileCreate,PhotographerProfileResponse, PhotographerProfileUpdate
from app.services.photographer_service import create_photographer_profile, get_photographer_profile, update_photographer_profile




router = APIRouter(prefix="/api/photographers",tags=["Photographers"],)


CurrentPhotographer = Annotated[User, Depends(get_current_photographer),]

DatabaseSession = Annotated[Session, Depends(get_db),]




@router.post("/me/profile", response_model=PhotographerProfileResponse, status_code=status.HTTP_201_CREATED,)
def create_profile(data : PhotographerProfileCreate, current_user : CurrentPhotographer,db : DatabaseSession,):
    
    try:
        return create_photographer_profile(db = db, user = current_user, data = data,)
    
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc




@router.get(
    "/me/profile",
    response_model=PhotographerProfileResponse,
)
def get_my_profile(
    current_user: CurrentPhotographer,
    db: DatabaseSession,
):
    profile = get_photographer_profile(
        db=db,
        user_id=current_user.id,
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photographer profile not found",
        )

    return profile




@router.patch(
    "/me/profile",
    response_model=PhotographerProfileResponse,
)
def update_my_profile(
    data: PhotographerProfileUpdate,
    current_user: CurrentPhotographer,
    db: DatabaseSession,
):
    profile = update_photographer_profile(
        db=db,
        user_id=current_user.id,
        data=data,
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photographer profile not found",
        )

    return profile