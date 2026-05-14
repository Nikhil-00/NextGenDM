import hashlib
import hmac
import json
from fastapi import APIRouter, Request, Response, HTTPException, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import get_db
from app.models.webhook_event import WebhookEvent
from app.workers.tasks import process_webhook_task

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def verify_signature(payload: bytes, signature: str, secret: str = None) -> bool:
    key = (secret or settings.META_APP_SECRET).encode()
    expected = hmac.new(key, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f"sha256={expected}", signature)


def _verify_token_response(hub_mode, hub_verify_token, hub_challenge):
    if hub_mode == "subscribe" and hub_verify_token == settings.META_VERIFY_TOKEN:
        return Response(content=hub_challenge, media_type="text/plain")
    raise HTTPException(status_code=403, detail="Webhook verification failed")


@router.get("/meta")
def verify_webhook_meta(hub_mode: str = None, hub_verify_token: str = None, hub_challenge: str = None):
    return _verify_token_response(hub_mode, hub_verify_token, hub_challenge)


@router.get("/instagram")
def verify_webhook_instagram(hub_mode: str = None, hub_verify_token: str = None, hub_challenge: str = None):
    return _verify_token_response(hub_mode, hub_verify_token, hub_challenge)


async def _handle_payload(request: Request, db: Session, secret: str = None):
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")
    if signature and not verify_signature(body, signature, secret):
        raise HTTPException(status_code=403, detail="Invalid webhook signature")
    return json.loads(body)


async def _process_payload(payload: dict, db: Session):
    for entry in payload.get("entry", []):
        ig_account_id = entry.get("id")

        for change in entry.get("changes", []):
            if change.get("field") == "comments":
                value = change.get("value", {})
                event = WebhookEvent(
                    event_type="comment",
                    raw_payload={
                        "ig_account_id": ig_account_id,
                        "commenter_id": value.get("from", {}).get("id"),
                        "commenter_username": value.get("from", {}).get("username"),
                        "comment_text": value.get("text", ""),
                        "comment_id": value.get("id"),
                        "media_id": value.get("media", {}).get("id"),
                    },
                )
                db.add(event)
                db.commit()
                db.refresh(event)
                process_webhook_task.delay(str(event.id))

        for messaging in entry.get("messaging", []):
            sender_id = messaging.get("sender", {}).get("id")
            message = messaging.get("message", {})
            if message and sender_id and sender_id != ig_account_id:
                event = WebhookEvent(
                    event_type="dm",
                    raw_payload={
                        "ig_account_id": ig_account_id,
                        "sender_id": sender_id,
                        "message_text": message.get("text", ""),
                        "message_id": message.get("mid"),
                    },
                )
                db.add(event)
                db.commit()
                db.refresh(event)
                process_webhook_task.delay(str(event.id))

    return {"status": "ok"}


@router.post("/test/comment")
async def test_comment_webhook(
    ig_account_id: str,
    commenter_id: str,
    comment_text: str,
    media_id: str = "",
    db: Session = Depends(get_db),
):
    """Dev-only: simulate a comment webhook event without Meta sending it."""
    if not settings.DEBUG:
        raise HTTPException(status_code=404)
    payload = {
        "entry": [{
            "id": ig_account_id,
            "changes": [{
                "field": "comments",
                "value": {
                    "from": {"id": commenter_id, "username": "test_user"},
                    "text": comment_text,
                    "id": "test_comment_id",
                    "media": {"id": media_id},
                },
            }],
        }]
    }
    return await _process_payload(payload, db)


@router.post("/instagram")
async def handle_webhook_instagram(request: Request, db: Session = Depends(get_db)):
    payload = await _handle_payload(request, db, secret=settings.INSTAGRAM_APP_SECRET)
    return await _process_payload(payload, db)


@router.post("/meta")
async def handle_webhook(request: Request, db: Session = Depends(get_db)):
    body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")

    if not verify_signature(body, signature):
        raise HTTPException(status_code=403, detail="Invalid webhook signature")

    payload = json.loads(body)
    return await _process_payload(payload, db)
