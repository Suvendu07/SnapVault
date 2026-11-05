from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.photographer_profile import PhotographerProfile
from app.models.user import User
from app.schemas.photographer import PhotographerProfileCreate, PhotographerProfileUpdate





def create_photographer_profile(db : Session, user : User, data : PhotographerProfileCreate,) -> PhotographerProfile:
    
    existing_profile = db.scalar(select(PhotographerProfile).where(PhotographerProfile.user_id == user.id))
    
    if existing_profile is not None:
        raise ValueError("Photographer profile already exists")
    
    profile_data = data.model_dump()
    
    if profile_data.get("website") is not None:
        profile_data["website"] = str(profile_data["website"])
        
    profile = PhotographerProfile(user_id = user.id, **profile_data,)
    
    db.add(profile)
    db.commit()
    db.refresh(profile)
    
    return profile



def get_photographer_profile(db : Session, user_id = UUID,) -> PhotographerProfile | None:
    
    statement = select(PhotographerProfile).where(PhotographerProfile.user_id == user_id)
    
    return db.scalar(statement)


def update_photographer_profile(db : Session, user_id : UUID, data : PhotographerProfileUpdate,) -> PhotographerProfile | None:
    
    profile = get_photographer_profile(db = db, user_id=user_id,)
    
    if profile is None:
        return None
    
    
    update_data = data.model_dump(exclude_unset=True)
    
    
    if "website" in update_data and update_data["website"] is not None:
        update_data["website"] = str(update_data["website"])

    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    return profile