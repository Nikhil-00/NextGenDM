import math
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.logs import PaginatedLogsResponse
from app.services.automation_service import get_logs

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("/", response_model=PaginatedLogsResponse)
def list_logs(
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items, total = get_logs(db, current_user.id, page, per_page)
    pages = math.ceil(total / per_page) if total > 0 else 1
    return PaginatedLogsResponse(items=items, total=total, page=page, per_page=per_page, pages=pages)
