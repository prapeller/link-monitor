from celery_app import celery_app
from core.config import settings
from database import SessionLocal
from database.crud import create
from database.models import init_models
from database.models.user import UserModel
from database.schemas.user import UserCreateSerializer
from services.keycloak.keycloak import KCAdmin


@celery_app.task(name='fetch_user_from_keycloak')
def fetch_user_from_keycloak():
    kc_admin = KCAdmin()
    user_ser = UserCreateSerializer(
        email=settings.SUPERUSER_EMAIL,
        first_name=settings.SUPERUSER_FIRST_NAME,
        last_name=settings.SUPERUSER_LAST_NAME,
    )
    kc_user_uuid = kc_admin.get_user_uuid_by_email(user_ser.email)
    user_ser.uuid = kc_user_uuid
    user_ser.is_head = True

    init_models()
    session = SessionLocal()
    create(session, UserModel, user_ser)
    session.close()
