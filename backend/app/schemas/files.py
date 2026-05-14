import uuid
from datetime import datetime
from pydantic import BaseModel


class FileResponse(BaseModel):
    id: uuid.UUID
    filename: str
    original_filename: str
    file_url: str
    file_size: int | None
    mime_type: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
