import uuid
from datetime import datetime
from pydantic import BaseModel


class InstagramAccountResponse(BaseModel):
    id: uuid.UUID
    instagram_user_id: str
    username: str
    profile_picture_url: str | None
    page_id: str | None
    page_name: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
