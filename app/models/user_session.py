import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class UserSession(Base):
    __tablename__ = "user_sessions"
    
    __table_args__ = (
        Index("ix_user_sessions_user_id", "user_id"),
    )
    
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True),
                                          primary_key=True,
                                          default=uuid.uuid4,)
    
    user_id : Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True),
                                                ForeignKey("users.id", ondelete = "CASCADE"),
                                                nullable=False,
                                                )
    
    token_hash : Mapped[str] = mapped_column(String(64), unique=True, nullable=False,)
    
    expire_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,)
    
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(),)
    
    revoke_at : Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True,)