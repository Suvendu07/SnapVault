import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, INTEGER, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    __tablename__ = "users"
    
    id : Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4,)
    full_name : Mapped[str] = mapped_column(String(150), nullable=False)
    email : Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False,)
    password_hash : Mapped[str] = mapped_column(String(255), nullable=False,)
    role : Mapped[str] = mapped_column(String(30), nullable = False, default = "photographer", server_default="photographer",)
    is_email_verified : Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false",)
    is_active : Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true",)
    created_at :Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,server_default=func.now(),)
    updated_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now(),)