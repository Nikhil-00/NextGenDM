import json
import uuid
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import redis as redis_lib

from app.models.instagram_account import InstagramAccount
from app.services import meta_api
from app.core.config import settings

redis_client = redis_lib.from_url(settings.REDIS_URL, decode_responses=True)

FOLLOWERS_CACHE_TTL = 1800  # 30 minutes


async def connect_instagram_account(user_id: uuid.UUID, code: str, db: Session) -> InstagramAccount:
    token_data = await meta_api.exchange_code_for_token(code)
    short_token = token_data["access_token"]

    long_token_data = await meta_api.get_long_lived_token(short_token)
    long_token = long_token_data["access_token"]
    expires_in = long_token_data.get("expires_in", 5183944)

    pages = await meta_api.get_facebook_pages(long_token)
    if not pages:
        raise HTTPException(status_code=400, detail="No Facebook Pages found. Link your Instagram Business account to a Facebook Page first.")

    ig_account_data = None
    connected_page = None
    for page in pages:
        ig = page.get("instagram_business_account")
        if ig:
            ig_account_data = ig
            connected_page = page
            break

    if not ig_account_data:
        raise HTTPException(status_code=400, detail="No Instagram Business account linked to your Facebook Pages.")

    existing = db.query(InstagramAccount).filter(
        InstagramAccount.instagram_user_id == str(ig_account_data["id"]),
        InstagramAccount.user_id == user_id,
    ).first()

    ig_user_id = str(ig_account_data["id"])

    if existing:
        existing.access_token = long_token
        existing.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        existing.username = ig_account_data.get("username", existing.username)
        existing.profile_picture_url = ig_account_data.get("profile_picture_url")
        existing.is_active = True
        db.commit()
        db.refresh(existing)
        try:
            await meta_api.subscribe_ig_account_webhooks(ig_user_id, long_token)
        except Exception:
            pass
        return existing

    account = InstagramAccount(
        user_id=user_id,
        instagram_user_id=ig_user_id,
        username=ig_account_data.get("username", "unknown"),
        profile_picture_url=ig_account_data.get("profile_picture_url"),
        access_token=long_token,
        token_expires_at=datetime.utcnow() + timedelta(seconds=expires_in),
        page_id=connected_page.get("id"),
        page_name=connected_page.get("name"),
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    try:
        await meta_api.subscribe_ig_account_webhooks(ig_user_id, long_token)
    except Exception:
        pass
    return account


async def check_user_follows(ig_account_id: str, commenter_id: str, access_token: str) -> bool:
    """
    Check if commenter follows the Instagram account.
    Uses Redis cache (30 min TTL) to avoid hitting Meta API rate limits.
    NOTE: Meta API limitation — this fetches the full followers list (paginated).
    For accounts with 100k+ followers, consider this a best-effort check.
    """
    cache_key = f"followers:{ig_account_id}"
    cached = redis_client.get(cache_key)

    if cached:
        followers_set = set(json.loads(cached))
        return commenter_id in followers_set

    followers_ids: list[str] = []
    cursor: Optional[str] = None
    max_pages = 10  # Safety cap to respect rate limits (~2000 followers max)

    for _ in range(max_pages):
        try:
            data = await meta_api.get_followers_page(ig_account_id, access_token, cursor)
            for follower in data.get("data", []):
                followers_ids.append(follower["id"])
            paging = data.get("paging", {})
            next_cursor = paging.get("cursors", {}).get("after")
            if not next_cursor or not paging.get("next"):
                break
            cursor = next_cursor
        except Exception:
            break

    redis_client.setex(cache_key, FOLLOWERS_CACHE_TTL, json.dumps(followers_ids))
    return commenter_id in set(followers_ids)
