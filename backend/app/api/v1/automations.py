import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.automation import AutomationCreate, AutomationUpdate, AutomationResponse
from app.services.automation_service import (
    create_automation, get_automations, get_automation,
    update_automation, delete_automation, toggle_automation,
)

router = APIRouter(prefix="/automations", tags=["automations"])


@router.get("/", response_model=list[AutomationResponse])
def list_automations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_automations(db, current_user.id)


@router.post("/", response_model=AutomationResponse, status_code=201)
def create(
    data: AutomationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_automation(db, current_user.id, data)


@router.get("/{automation_id}", response_model=AutomationResponse)
def get_one(
    automation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_automation(db, automation_id, current_user.id)


@router.put("/{automation_id}", response_model=AutomationResponse)
def update(
    automation_id: uuid.UUID,
    data: AutomationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return update_automation(db, automation_id, current_user.id, data)


@router.delete("/{automation_id}")
def delete(
    automation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    delete_automation(db, automation_id, current_user.id)
    return {"message": "Automation deleted"}


@router.patch("/{automation_id}/toggle", response_model=AutomationResponse)
def toggle(
    automation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return toggle_automation(db, automation_id, current_user.id)
