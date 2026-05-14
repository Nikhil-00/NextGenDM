import uuid
from datetime import datetime
from pydantic import BaseModel
from app.models.automation_log import LogStatus


class LogResponse(BaseModel):
    id: uuid.UUID
    automation_id: uuid.UUID | None
    trigger_type: str | None
    trigger_keyword: str | None
    sender_instagram_id: str | None
    sender_username: str | None
    action_taken: str | None
    status: LogStatus
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedLogsResponse(BaseModel):
    items: list[LogResponse]
    total: int
    page: int
    per_page: int
    pages: int
