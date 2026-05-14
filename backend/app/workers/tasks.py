import asyncio
import uuid
from app.workers.celery_app import celery_app
from app.database.session import SessionLocal
from app.models.instagram_account import InstagramAccount
from app.models.automation import Automation, TriggerType
from app.models.automation_log import AutomationLog, LogStatus
from app.models.webhook_event import WebhookEvent


def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_dm_task(self, ig_user_id: str, recipient_id: str, message: str, access_token: str, log_id: str = None):
    from app.services.meta_api import send_instagram_dm, get_page_access_token
    db = SessionLocal()
    try:
        account = db.query(InstagramAccount).filter(
            InstagramAccount.instagram_user_id == ig_user_id,
            InstagramAccount.is_active == True,
        ).first()
        if not account or not account.page_id:
            raise ValueError(f"No active account with page_id for ig_user {ig_user_id}")
        page_token = run_async(get_page_access_token(account.page_id, account.access_token))
        run_async(send_instagram_dm(account.page_id, recipient_id, message, page_token))
        if log_id:
            log = db.query(AutomationLog).filter(AutomationLog.id == uuid.UUID(log_id)).first()
            if log:
                log.status = LogStatus.SUCCESS
                db.commit()
    except Exception as exc:
        if log_id:
            log = db.query(AutomationLog).filter(AutomationLog.id == uuid.UUID(log_id)).first()
            if log:
                log.status = LogStatus.FAILED
                log.error_message = str(exc)
                db.commit()
        raise self.retry(exc=exc)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def process_webhook_task(self, event_id: str):
    db = SessionLocal()
    try:
        event = db.query(WebhookEvent).filter(WebhookEvent.id == uuid.UUID(event_id)).first()
        if not event or event.processed:
            return

        if event.event_type == "comment":
            _process_comment_event(db, event.raw_payload)
        elif event.event_type == "dm":
            _process_dm_event(db, event.raw_payload)

        event.processed = True
        db.commit()
    except Exception as exc:
        event = db.query(WebhookEvent).filter(WebhookEvent.id == uuid.UUID(event_id)).first()
        if event:
            event.error = str(exc)
            db.commit()
        raise self.retry(exc=exc)
    finally:
        db.close()


def _get_active_account(db, ig_account_id: str):
    return db.query(InstagramAccount).filter(
        InstagramAccount.instagram_user_id == ig_account_id,
        InstagramAccount.is_active == True,
    ).first()


def _process_comment_event(db, payload: dict):
    from app.services.instagram_service import check_user_follows

    ig_account_id = payload.get("ig_account_id")
    commenter_id = payload.get("commenter_id")
    comment_text = (payload.get("comment_text") or "").lower().strip()
    event_media_id = payload.get("media_id")

    account = _get_active_account(db, ig_account_id)
    if not account:
        return

    automations = db.query(Automation).filter(
        Automation.instagram_account_id == account.id,
        Automation.trigger_type == TriggerType.COMMENT_KEYWORD,
        Automation.is_active == True,
        Automation.deleted_at.is_(None),
    ).all()

    for automation in automations:
        keyword = automation.trigger_keyword.lower().strip()
        if keyword not in comment_text and comment_text != keyword:
            continue

        # If automation targets a specific post, skip comments on other posts
        if automation.media_id and automation.media_id != event_media_id:
            continue

        log = AutomationLog(
            automation_id=automation.id,
            user_id=account.user_id,
            trigger_type="comment_keyword",
            trigger_keyword=automation.trigger_keyword,
            sender_instagram_id=commenter_id,
            action_taken="send_dm",
            status=LogStatus.PENDING,
        )
        db.add(log)
        db.commit()
        db.refresh(log)

        if automation.require_follow:
            follows = run_async(check_user_follows(ig_account_id, commenter_id, account.access_token))
            if not follows:
                log.status = LogStatus.FOLLOW_REQUIRED
                db.commit()
                send_dm_task.delay(
                    ig_account_id,
                    commenter_id,
                    automation.follow_required_message,
                    account.access_token,
                    str(log.id),
                )
                continue

        message = automation.response_message
        if automation.response_link:
            message = f"{message}\n\n{automation.response_link}"

        send_dm_task.delay(ig_account_id, commenter_id, message, account.access_token, str(log.id))


def _process_dm_event(db, payload: dict):
    ig_account_id = payload.get("ig_account_id")
    sender_id = payload.get("sender_id")
    message_text = (payload.get("message_text") or "").lower().strip()

    account = _get_active_account(db, ig_account_id)
    if not account:
        return

    automations = db.query(Automation).filter(
        Automation.instagram_account_id == account.id,
        Automation.trigger_type == TriggerType.DM_KEYWORD,
        Automation.is_active == True,
        Automation.deleted_at.is_(None),
    ).all()

    for automation in automations:
        keyword = automation.trigger_keyword.lower().strip()
        if keyword not in message_text and message_text != keyword:
            continue

        log = AutomationLog(
            automation_id=automation.id,
            user_id=account.user_id,
            trigger_type="dm_keyword",
            trigger_keyword=automation.trigger_keyword,
            sender_instagram_id=sender_id,
            action_taken="send_dm",
            status=LogStatus.PENDING,
        )
        db.add(log)
        db.commit()
        db.refresh(log)

        message = automation.response_message
        if automation.response_link:
            message = f"{message}\n\n{automation.response_link}"

        send_dm_task.delay(ig_account_id, sender_id, message, account.access_token, str(log.id))


@celery_app.task
def refresh_tokens_task():
    from datetime import datetime, timedelta
    from app.services.meta_api import get_long_lived_token

    db = SessionLocal()
    try:
        soon_expiring = db.query(InstagramAccount).filter(
            InstagramAccount.is_active == True,
            InstagramAccount.token_expires_at <= datetime.utcnow() + timedelta(days=7),
        ).all()

        for account in soon_expiring:
            try:
                data = run_async(get_long_lived_token(account.access_token))
                account.access_token = data["access_token"]
                account.token_expires_at = datetime.utcnow() + timedelta(seconds=data.get("expires_in", 5183944))
                db.commit()
            except Exception:
                pass
    finally:
        db.close()
