import uuid
from datetime import datetime, timedelta
from urllib.parse import urlencode
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.core.dependencies import get_current_user
from app.core.config import settings
from app.models.user import User
from app.models.instagram_account import InstagramAccount
from app.schemas.instagram import InstagramAccountResponse
from app.services.instagram_service import connect_instagram_account
from app.services import meta_api

router = APIRouter(prefix="/instagram", tags=["instagram"])

OAUTH_SCOPES = (
    "instagram_business_basic,"
    "instagram_business_manage_messages,"
    "instagram_business_manage_comments"
)


@router.get("/connect")
def initiate_oauth(current_user: User = Depends(get_current_user)):
    params = urlencode({
        "client_id": settings.INSTAGRAM_APP_ID,
        "redirect_uri": settings.INSTAGRAM_REDIRECT_URI,
        "scope": OAUTH_SCOPES,
        "response_type": "code",
        "state": str(current_user.id),
    })
    oauth_url = f"https://api.instagram.com/oauth/authorize?{params}"
    return {"oauth_url": oauth_url}


@router.get("/callback")
async def oauth_callback(code: str, state: str, db: Session = Depends(get_db)):
    try:
        user_id = uuid.UUID(state)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    account = await connect_instagram_account(user_id, code, db)
    return RedirectResponse(
        url=f"{settings.FRONTEND_URL}/instagram?connected=true&username={account.username}"
    )


@router.get("/accounts", response_model=list[InstagramAccountResponse])
def list_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(InstagramAccount).filter(
        InstagramAccount.user_id == current_user.id,
        InstagramAccount.is_active == True,
    ).all()


class ManualTokenRequest(BaseModel):
    access_token: str


@router.post("/connect/manual")
async def connect_manual_token(
    body: ManualTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Dev-only: connect Instagram account using a manually generated token."""
    try:
        ig_user = await meta_api.get_instagram_user(body.access_token)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid token or API error: {e}")

    existing = db.query(InstagramAccount).filter(
        InstagramAccount.instagram_user_id == str(ig_user["id"]),
        InstagramAccount.user_id == current_user.id,
    ).first()

    if existing:
        existing.access_token = body.access_token
        existing.token_expires_at = datetime.utcnow() + timedelta(days=60)
        existing.username = ig_user.get("username", existing.username)
        existing.profile_picture_url = ig_user.get("profile_picture_url")
        existing.is_active = True
        db.commit()
        db.refresh(existing)
        return existing

    account = InstagramAccount(
        user_id=current_user.id,
        instagram_user_id=str(ig_user["id"]),
        username=ig_user.get("username", "unknown"),
        profile_picture_url=ig_user.get("profile_picture_url"),
        access_token=body.access_token,
        token_expires_at=datetime.utcnow() + timedelta(days=60),
        page_id=None,
        page_name=ig_user.get("name"),
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.get("/accounts/{account_id}/media")
async def get_account_media(
    account_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = db.query(InstagramAccount).filter(
        InstagramAccount.id == account_id,
        InstagramAccount.user_id == current_user.id,
        InstagramAccount.is_active == True,
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    try:
        media = await meta_api.get_user_media(account.instagram_user_id, account.access_token)
        return media
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch media: {e}")


@router.delete("/accounts/{account_id}")
def disconnect_account(
    account_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = db.query(InstagramAccount).filter(
        InstagramAccount.id == account_id,
        InstagramAccount.user_id == current_user.id,
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    account.is_active = False
    db.commit()
    return {"message": "Account disconnected successfully"}
