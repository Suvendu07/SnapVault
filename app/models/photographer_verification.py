import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text, Uuid, func

from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base



class PhotographerVerification(Base):
    
    __tablename__ = "photographer_verifications"
    
    __table_args__ = (CheckConstraint("status IN ('pending', 'approved', 'rejected',)",name="ck_photographer_verifications_status"), Index("ix_photographer_verifications_user_id", "user_id",), Index("ix_photographer_verifications_status","status"),)
    
    id : Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4,)
    
    user_id : Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False,)
    
    portfolio_url : Mapped[str | None] = mapped_column(String(255), nullable=True,)
    
    message : Mapped[str | None] = mapped_column(Text, nullable=True,)
    
    status : Mapped[str] = mapped_column(String(20), nullable=False, default="pending", server_default="pending",)
    
    rejection_reason : Mapped[str | None] = mapped_column(Text, nullable=True,)
    
    reviewed_by : Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True,)
    
    submitted_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(),)
    
    reviewed_at : Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True,)
    
    created_at : Mapped[datetime] = mapped_column(DateTime(timezone=True),nullable=False, server_default=func.now(),)