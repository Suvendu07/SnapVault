import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PhotographerProfile(Base):
    
    __tablename__ = "photographer_profiles"
    
    id : Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4,)
    
    user_id : Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True),ForeignKey("users.id", ondelete="CASCADE"),unique=True, nullable=False,)
    
    business_name : Mapped[str | None] = mapped_column(String(150), nullable=True,)
    
    phone_number : Mapped[str | None] = mapped_column(String(20), nullable=True,)
    
    bio : Mapped[str | None] = mapped_column(Text, nullable=True,)
    
    website : Mapped[str | None] = mapped_column(String(255), nullable=True,)
    
    city : Mapped[str | None] = mapped_column(String(100), nullable=True,)
    
    state : Mapped[str | None] = mapped_column(String(100), nullable=True,)
    
    country : Mapped[str | None] = mapped_column(String(100), nullable=True,)
    
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(),)
    
    updated_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now(),)
    
    verification_status : Mapped[str] = mapped_column(String(20), nullable=False, default="not_submitted", server_default="not_submitted",)
    
    verified_at : Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True,)