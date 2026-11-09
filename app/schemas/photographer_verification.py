from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl




class VerificationRequestCreate(BaseModel):
    
    portfolio_url : HttpUrl | None = None
    message : str | None = Field(default=None, max_length=1000)
    

class VerificationRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id : UUID
    user_id : UUID
    portfolio_url : str | None
    message : str | None
    status : str
    rejection_reason : str | None
    submitted_at : datetime
    reviewed_at : datetime | None