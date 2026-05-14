import uuid
import enum
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.database.base import Base


class TriggerType(str, enum.Enum):
    COMMENT_KEYWORD = "comment_keyword"
    DM_KEYWORD = "dm_keyword"


class ActionType(str, enum.Enum):
    SEND_DM = "send_dm"
    SEND_LINK = "send_link"


class Automation(Base):
    __tablename__ = "automations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    instagram_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("instagram_accounts.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    trigger_type: Mapped[TriggerType] = mapped_column(SAEnum(TriggerType), nullable=False)
    trigger_keyword: Mapped[str] = mapped_column(String(255), nullable=False)
    action_type: Mapped[ActionType] = mapped_column(SAEnum(ActionType), nullable=False)
    response_message: Mapped[str] = mapped_column(Text, nullable=False)
    response_link: Mapped[str | None] = mapped_column(String(1000))
    require_follow: Mapped[bool] = mapped_column(Boolean, default=False)
    follow_required_message: Mapped[str] = mapped_column(
        Text, default="Please follow our account first to receive this content!"
    )
    media_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    media_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user = relationship("User", back_populates="automations")
    instagram_account = relationship("InstagramAccount", back_populates="automations")
    logs = relationship("AutomationLog", back_populates="automation", lazy="dynamic")
