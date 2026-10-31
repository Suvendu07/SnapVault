import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Uuid, func

from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base



class UserToken(Base):
    
    __tablename__ = "user_tokens"
    
    __table_args__ = (
        Index("ix_user_tokens_user_purpose", "user_id", "purpose"),
    )
    
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4,)
    
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCade"), nullable=False,)
    
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False,)
    
    purpose: Mapped[str] = mapped_column(String(30), nullable=False,)
    
    expire_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,)
    
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True,)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(),)
    
    