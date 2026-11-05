from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator



class PhotographerProfileCreate(BaseModel):
    
    business_name : str | None = Field(default=None, max_length=150)
    
    phone_number : str | None = Field(default=None, max_length=20)
    
    bio : str | None = Field(default=None, max_length=1000)
    
    website : HttpUrl | None = None
    
    city : str | None = Field(default=None, max_length=100)
    
    state : str | None = Field(default=None, max_length=100)
    
    country : str | None = Field(default=None, max_length=100)
    
    @field_validator(
        "business_name", "phone_number", "bio","city","state","country",
    )
    @classmethod
    def strip_value(cls, value : str | None) -> str | None:
        
        if value is None:
            return None
        
        value = value.strip()
        
        return value or None
    




class PhotographerProfileUpdate(PhotographerProfileCreate):
    pass


class PhotographerProfileResponse(BaseModel):
    
    model_config = ConfigDict(from_attributes=True)
    
    id : UUID
    user_id : UUID
    business_name : str | None
    phone_number : str | None
    bio : str | None
    website : HttpUrl | None
    city : str | None
    state : str | None
    country : str | None
    created_at : datetime
    updated_at : datetime