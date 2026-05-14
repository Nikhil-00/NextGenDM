import uuid
from datetime import datetime
from pydantic import BaseModel
from app.models.automation import TriggerType, ActionType


class AutomationCreate(BaseModel):
    instagram_account_id: uuid.UUID
    name: str
    trigger_type: TriggerType
    trigger_keyword: str
    action_type: ActionType
    response_message: str
    response_link: str | None = None
    require_follow: bool = False
    follow_required_message: str = "Please follow our account first to receive this content!"
    media_id: str | None = None
    media_url: str | None = None


class AutomationUpdate(BaseModel):
    name: str | None = None
    trigger_keyword: str | None = None
    response_message: str | None = None
    response_link: str | None = None
    require_follow: bool | None = None
    follow_required_message: str | None = None
    is_active: bool | None = None


class AutomationResponse(BaseModel):
    id: uuid.UUID
    instagram_account_id: uuid.UUID
    name: str
    trigger_type: TriggerType
    trigger_keyword: str
    action_type: ActionType
    response_message: str
    response_link: str | None
    require_follow: bool
    follow_required_message: str
    media_id: str | None
    media_url: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
