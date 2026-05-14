from fastapi import APIRouter
from app.api.v1 import auth, users, instagram, automations, webhooks, logs, files, dashboard

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(instagram.router)
api_router.include_router(automations.router)
api_router.include_router(webhooks.router)
api_router.include_router(logs.router)
api_router.include_router(files.router)
api_router.include_router(dashboard.router)
