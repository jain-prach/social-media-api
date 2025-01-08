from __future__ import absolute_import, unicode_literals

from celery import Celery

from src.setup.config.settings import settings
from lib.fastapi.utils import get_default_timezone

app = Celery(
    "scheduler",
    include=["src.application.users.tasks"],
    backend=settings.CELERY_BACKEND_URL,
    broker=settings.CELERY_BROKER_URL,
)

app.conf.update(timezone=get_default_timezone())
