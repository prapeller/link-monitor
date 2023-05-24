from celery_app import celery_app
from database.models import init_models
from services.notificator.notificator import logger, Notificator


@celery_app.task(name='prepare_and_send_linkers_report_daily_messages')
def prepare_and_send_linkers_report_daily_messages():
    init_models()
    with Notificator() as notificator:
        logger.debug(f'prepare_and_send_linkers_report_daily_messages')
        notificator.prepare_and_send_linkers_report_daily_messages()


@celery_app.task(name='prepare_and_send_content_author_todo_messages')
def prepare_and_send_content_author_todo_messages():
    init_models()
    with Notificator() as notificator:
        logger.debug(f'prepare_and_send_content_author_todo_messages')
        notificator.prepare_and_send_content_author_todo_messages()


@celery_app.task(name='prepare_and_send_content_author_changed_to_edit_messages')
def prepare_and_send_content_author_changed_to_edit_messages():
    init_models()
    with Notificator() as notificator:
        logger.debug(f'prepare_and_send_content_author_changed_to_edit_messages')
        notificator.prepare_and_send_content_author_changed_to_edit_messages()


@celery_app.task(name='prepare_and_send_content_author_deadline_overdue_messages')
def prepare_and_send_content_author_deadline_overdue_messages():
    init_models()
    with Notificator() as notificator:
        logger.debug(f'prepare_and_send_content_author_deadline_overdue_messages')
        notificator.prepare_and_send_content_author_deadline_overdue_messages()


@celery_app.task(name='prepare_and_send_content_author_and_teamlead_are_idle_messages')
def prepare_and_send_content_author_and_teamlead_are_idle_messages():
    init_models()
    with Notificator() as notificator:
        logger.debug(f'prepare_and_send_content_author_and_teamlead_are_idle_messages')
        notificator.prepare_and_send_content_author_and_teamlead_are_idle_messages()
