"""
Run this script once whenever your ngrok URL changes, or when deploying to a new server.

Usage (from backend/ directory, with venv activated):
    python setup_webhook.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.core.config import settings
from app.services import meta_api
from app.database.session import SessionLocal
from app.models.instagram_account import InstagramAccount


async def main():
    callback_url = f"{settings.BACKEND_URL}/api/v1/webhooks/meta"
    print(f"Step 1: Registering app-level Instagram webhook...")
    print(f"  Callback URL : {callback_url}")
    print(f"  Verify token : {settings.META_VERIFY_TOKEN}")

    try:
        await meta_api.register_app_instagram_webhook(callback_url, settings.META_VERIFY_TOKEN)
        print("  App-level webhook registered.\n")
    except Exception as e:
        print(f"  FAILED: {e}\n")
        return

    db = SessionLocal()
    try:
        accounts = db.query(InstagramAccount).filter(InstagramAccount.is_active == True).all()
        if not accounts:
            print("No active Instagram accounts found.")
            return

        print(f"Step 2: Subscribing {len(accounts)} account(s) to webhook events...")
        for account in accounts:
            # Try IG-user endpoint first
            try:
                await meta_api.subscribe_ig_account_webhooks(
                    account.instagram_user_id,
                    account.access_token,
                )
                print(f"  Subscribed (IG user): @{account.username}")
                continue
            except Exception as e1:
                print(f"  IG-user subscription failed for @{account.username}: {e1}")

            # Fallback: try page endpoint using a fresh page token
            if account.page_id:
                try:
                    pages = await meta_api.get_facebook_pages(account.access_token)
                    page_token = next(
                        (p["access_token"] for p in pages if p["id"] == account.page_id),
                        None,
                    )
                    if not page_token:
                        print(f"  Could not get page token for @{account.username}")
                        continue
                    await meta_api.subscribe_page_webhooks(account.page_id, page_token)
                    print(f"  Subscribed (page): @{account.username}")
                except Exception as e2:
                    print(f"  Page subscription also failed for @{account.username}: {e2}")
            else:
                print(f"  No page_id stored for @{account.username}, skipping.")
    finally:
        db.close()

    print("\nDone.")


if __name__ == "__main__":
    asyncio.run(main())
