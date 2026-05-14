import math
import uuid
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.automation import Automation
from app.models.automation_log import AutomationLog, LogStatus
from app.schemas.automation import AutomationCreate, AutomationUpdate


def create_automation(db: Session, user_id: uuid.UUID, data: AutomationCreate) -> Automation:
    automation = Automation(user_id=user_id, **data.model_dump())
    db.add(automation)
    db.commit()
    db.refresh(automation)
    return automation


def get_automations(db: Session, user_id: uuid.UUID) -> list[Automation]:
    return (
        db.query(Automation)
        .filter(Automation.user_id == user_id, Automation.deleted_at.is_(None))
        .order_by(Automation.created_at.desc())
        .all()
    )


def get_automation(db: Session, automation_id: uuid.UUID, user_id: uuid.UUID) -> Automation:
    automation = db.query(Automation).filter(
        Automation.id == automation_id,
        Automation.user_id == user_id,
        Automation.deleted_at.is_(None),
    ).first()
    if not automation:
        raise HTTPException(status_code=404, detail="Automation not found")
    return automation


def update_automation(db: Session, automation_id: uuid.UUID, user_id: uuid.UUID, data: AutomationUpdate) -> Automation:
    automation = get_automation(db, automation_id, user_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(automation, field, value)
    automation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(automation)
    return automation


def delete_automation(db: Session, automation_id: uuid.UUID, user_id: uuid.UUID) -> None:
    automation = get_automation(db, automation_id, user_id)
    automation.deleted_at = datetime.utcnow()
    db.commit()


def toggle_automation(db: Session, automation_id: uuid.UUID, user_id: uuid.UUID) -> Automation:
    automation = get_automation(db, automation_id, user_id)
    automation.is_active = not automation.is_active
    db.commit()
    db.refresh(automation)
    return automation


def get_logs(db: Session, user_id: uuid.UUID, page: int = 1, per_page: int = 20) -> tuple:
    query = db.query(AutomationLog).filter(AutomationLog.user_id == user_id)
    total = query.count()
    items = (
        query.order_by(AutomationLog.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return items, total


def get_dashboard_stats(db: Session, user_id: uuid.UUID) -> dict:
    from app.models.instagram_account import InstagramAccount
    total_automations = db.query(Automation).filter(
        Automation.user_id == user_id, Automation.deleted_at.is_(None)
    ).count()
    active_automations = db.query(Automation).filter(
        Automation.user_id == user_id,
        Automation.is_active == True,
        Automation.deleted_at.is_(None),
    ).count()
    connected_accounts = db.query(InstagramAccount).filter(
        InstagramAccount.user_id == user_id,
        InstagramAccount.is_active == True,
    ).count()
    messages_sent = db.query(AutomationLog).filter(
        AutomationLog.user_id == user_id,
        AutomationLog.status == LogStatus.SUCCESS,
    ).count()
    return {
        "total_automations": total_automations,
        "active_automations": active_automations,
        "connected_accounts": connected_accounts,
        "messages_sent": messages_sent,
    }
