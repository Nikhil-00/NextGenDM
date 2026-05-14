import httpx
from typing import Optional
from app.core.config import settings

FB_BASE = f"https://graph.facebook.com/{settings.META_API_VERSION}"
IG_BASE = f"https://graph.instagram.com/{settings.META_API_VERSION}"


async def exchange_code_for_token(code: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.instagram.com/oauth/access_token",
            data={
                "client_id": settings.INSTAGRAM_APP_ID,
                "client_secret": settings.INSTAGRAM_APP_SECRET,
                "grant_type": "authorization_code",
                "redirect_uri": settings.INSTAGRAM_REDIRECT_URI,
                "code": code,
            },
        )
        response.raise_for_status()
        return response.json()


async def get_long_lived_token(short_lived_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{IG_BASE}/access_token",
            params={
                "grant_type": "ig_exchange_token",
                "client_id": settings.INSTAGRAM_APP_ID,
                "client_secret": settings.INSTAGRAM_APP_SECRET,
                "access_token": short_lived_token,
            },
        )
        response.raise_for_status()
        return response.json()


async def get_facebook_pages(access_token: str) -> list[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{FB_BASE}/me/accounts",
            params={
                "access_token": access_token,
                "fields": "id,name,access_token,instagram_business_account{id,username,profile_picture_url,followers_count}",
            },
        )
        response.raise_for_status()
        return response.json().get("data", [])


async def get_instagram_user(access_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{IG_BASE}/me",
            params={
                "fields": "id,name,username,profile_picture_url,followers_count",
                "access_token": access_token,
            },
        )
        response.raise_for_status()
        return response.json()


async def get_user_media(ig_user_id: str, access_token: str) -> list[dict]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{FB_BASE}/{ig_user_id}/media",
            params={
                "fields": "id,caption,media_type,media_url,thumbnail_url,permalink,timestamp",
                "limit": 20,
                "access_token": access_token,
            },
        )
        response.raise_for_status()
        return response.json().get("data", [])


async def get_page_access_token(page_id: str, user_access_token: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{FB_BASE}/{page_id}",
            params={"fields": "access_token", "access_token": user_access_token},
        )
        if not response.is_success:
            raise Exception(f"Failed to get page token: {response.text}")
        token = response.json().get("access_token")
        if not token:
            raise Exception(f"No access_token returned for page {page_id}")
        return token


async def send_instagram_dm(page_id: str, recipient_id: str, message: str, page_access_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{FB_BASE}/{page_id}/messages",
            json={
                "recipient": {"id": recipient_id},
                "message": {"text": message},
            },
            params={"access_token": page_access_token},
        )
        if not response.is_success:
            raise Exception(f"{response.status_code}: {response.text}")
        return response.json()


async def reply_to_comment(comment_id: str, message: str, access_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{FB_BASE}/{comment_id}/replies",
            params={"access_token": access_token},
            json={"message": message},
        )
        response.raise_for_status()
        return response.json()


async def subscribe_ig_account_webhooks(ig_user_id: str, access_token: str) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{IG_BASE}/{ig_user_id}/subscribed_apps",
            params={
                "subscribed_fields": "comments,messages",
                "access_token": access_token,
            },
        )
        if not response.is_success:
            raise Exception(f"{response.status_code}: {response.text}")
        response.raise_for_status()


async def subscribe_page_webhooks(page_id: str, page_access_token: str) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{FB_BASE}/{page_id}/subscribed_apps",
            params={
                "subscribed_fields": "feed,messages",
                "access_token": page_access_token,
            },
        )
        if not response.is_success:
            raise Exception(f"{response.status_code}: {response.text}")
        response.raise_for_status()


async def register_app_instagram_webhook(callback_url: str, verify_token: str) -> None:
    app_token = f"{settings.META_APP_ID}|{settings.META_APP_SECRET}"
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{FB_BASE}/{settings.META_APP_ID}/subscriptions",
            params={
                "object": "instagram",
                "callback_url": callback_url,
                "fields": "comments,messages",
                "verify_token": verify_token,
                "access_token": app_token,
            },
        )
        response.raise_for_status()


async def get_followers_page(ig_user_id: str, access_token: str, cursor: Optional[str] = None) -> dict:
    params: dict = {
        "access_token": access_token,
        "fields": "id,username",
        "limit": 200,
    }
    if cursor:
        params["after"] = cursor
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FB_BASE}/{ig_user_id}/followers", params=params)
        response.raise_for_status()
        return response.json()
