from __future__ import absolute_import, unicode_literals

from celery import Celery
from celery.schedules import crontab

from src.setup.config.settings import settings
from lib.fastapi.utils import get_default_timezone

app = Celery(
    "scheduler",
    include=["src.application.users.tasks", "src.application.posts.tasks"],
    backend=settings.CELERY_BACKEND_URL,
    broker=settings.CELERY_BROKER_URL,
)

app.conf.update(timezone=get_default_timezone())

app.conf.update(beat_schedule={
    'add_everyday_at_10':{
        'task': 'src.application.posts.tasks.schedule_post_notifications',
        'schedule': crontab(minute="51", hour="17"),
    }
})