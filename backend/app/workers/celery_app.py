from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "nextgendm",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    task_routes={},
)

celery_app.conf.beat_schedule = {
    "refresh-tokens-daily": {
        "task": "app.workers.tasks.refresh_tokens_task",
        "schedule": 86400.0,
    },
}
