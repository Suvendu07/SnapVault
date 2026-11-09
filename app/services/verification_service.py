from fastapi import HTTPException,status
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.photographer_profile import PhotographerProfile
from app.models.photographer_verification import PhotographerVerification
from app.schemas.photographer_verification import VerificationRequestCreate




def submit_verification_request(db : Session, user_id : UUID, data : VerificationRequestCreate,) -> PhotographerVerification:
    
    profile = db.scalar(select(PhotographerProfile).where(PhotographerProfile.user_id == user_id))
    
    if profile is None:
         raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Please create your photographer profile first."
    )
         
    if profile.verification_status == "approved":
       raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Your photographer account is already verified."
    )

    if profile.verification_status == "pending":
      raise HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="You already have a pending verification request."
    )
      
    request = PhotographerVerification(
        user_id = user_id,
        portfolio_url = (
            str(data.portfolio_url)
            if data.portfolio_url is not None
            else None
        ),
        message = data.message,
        status = "pending",
    )
    
    profile.verification_status = "pending"
    profile.verified_at = None
    
    try:
        db.add(request)
        db.commit()
        db.refresh(request)
        
    except Exception:
         db.rollback()
         raise
    
    return request




def get_verification_status(db : Session, user_id : UUID,) -> PhotographerProfile | None:
    
    statement = select(PhotographerProfile).where(PhotographerProfile.user_id == user_id)
    
    return db.scalar(statement)