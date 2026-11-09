from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session


from app.core.dependencies import get_current_photographer
from app.db.session import get_db
from app.models.user import User
from app.schemas.photographer_verification import VerificationRequestCreate, VerificationRequestResponse
from app.services.verification_service import get_verification_status, submit_verification_request





router = APIRouter(prefix="/api/photographers", tags=["Photographer Verification"])

CurrentPhotographer = Annotated[
    User, Depends(get_current_photographer),
]

DatabaseSession = Annotated[
    Session, Depends(get_db),
]

@router.post("/me/verification",
             response_model=VerificationRequestResponse, status_code=status.HTTP_201_CREATED,)
def submit_verification(
    data : VerificationRequestCreate, current_user : CurrentPhotographer, db : DatabaseSession,
):
    
    return submit_verification_request(db=db, user_id=current_user.id, data=data,)
    
    
    

@router.get("/me/verification_status")
def my_verification_status(current_user : CurrentPhotographer, db : DatabaseSession,):
    
    profile= get_verification_status(db=db, user_id=current_user.id,)
    
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Photographer profile not found.",
        )
        
    return {
        "verification_status": profile.verification_status,
        "verified_at": profile.verified_at,
    }