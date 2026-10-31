from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class UserRegister(BaseModel):
    
    full_name : str = Field(min_length=2, max_length=150,)
    email : EmailStr
    password : str = Field(min_length=12, max_length=128,)
    
    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value : str) -> str:
        value = value.strip()
        
        if len(value) < 2:
            raise ValueError("Full name must contain at least 2 characters")
        
        return value
    
    
    @field_validator("email", mode = "before")
    @classmethod
    def normalized_email(cls, value : str) -> str:
        if not isinstance(value, str):
            raise ValueError("Email must be a string")
        
        return value.strip().lower()
    
    
    
class UserLogin(BaseModel):
    email : EmailStr
    password : str = Field(min_length=1, max_length=128)
    
    @field_validator("email", mode = "before")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("Email must be a string")
        
        return value.strip().lower()
    

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    email: EmailStr
    role: str
    is_email_verified: bool
    is_active: bool
    created_at: datetime
    
    
class LoginResponse(BaseModel):
    message: str
    user: UserResponse