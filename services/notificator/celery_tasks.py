from celery_app import celery_app
from database import SessionLocal
from database.models import init_models
from database.models.user import UserModel
from services.notificator.notificator import notify_users, logger


@celery_app.task(name='notify_users_all')
def notify_users_all():
    init_models()
    session = SessionLocal()
    users = session.query(UserModel).all()
    logger.debug(f'notify_users_all task: {users}')
    notify_users(session, users)
    session.close()
