import uuid
import enum
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database.base import Base


class LogStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    FOLLOW_REQUIRED = "follow_required"


class AutomationLog(Base):
    __tablename__ = "automation_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    automation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("automations.id", ondelete="SET NULL"), nullable=True, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    trigger_type: Mapped[str | None] = mapped_column(String(50))
    trigger_keyword: Mapped[str | None] = mapped_column(String(255))
    sender_instagram_id: Mapped[str | None] = mapped_column(String(100))
    sender_username: Mapped[str | None] = mapped_column(String(100))
    action_taken: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[LogStatus] = mapped_column(SAEnum(LogStatus), default=LogStatus.PENDING)
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    automation = relationship("Automation", back_populates="logs")
