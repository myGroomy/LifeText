"""Celery application setup."""
from celery import Celery
from src.config import get_settings

settings = get_settings()

celery_app = Celery(
    "lifetext",
    broker=settings.redis_url,
    backend=settings.redis_url
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour hard limit
)
