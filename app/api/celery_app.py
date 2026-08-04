from celery import Celery
from core.config import REDIS_URL
from celery.signals import setup_logging

@setup_logging.connect
def config_loggers(*args, **kwargs):
    pass

celery_app = Celery(
    "teacher_ai_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["api.worker"]
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True
)