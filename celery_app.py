import os

from celery import Celery

from core.config import settings

celery_app = Celery(__name__, broker=settings.CELERY_BROKER_URL, backend=settings.CELERY_RESULT_BACKEND)
celery_app.conf.beat_schedule = settings.CELERY_BEAT_SCHEDULE
celery_app.conf.timezone = settings.CELERY_TIMEZONE


def import_celery_tasks_from_services():
    root, subdirs, files = next(os.walk(f'{os.getcwd()}/services/'))
    for dir in subdirs:
        try:
            exec(f'from services.{dir} import celery_tasks')
        except ImportError:
            continue


import_celery_tasks_from_services()
