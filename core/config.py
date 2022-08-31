import os
import secrets
from collections import OrderedDict

from celery.schedules import crontab
from typing import List
from pathlib import Path

from pydantic import BaseSettings, AnyHttpUrl, EmailStr


class Settings(BaseSettings):
    BASE_DIR = Path(__file__).resolve().parent.parent
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / '.envs/.prod')

    SECRET_KEY: str = secrets.token_urlsafe(32)

    SUPERUSER_EMAIL = os.getenv('SUPERUSER_EMAIL', 'pavelmirosh@gmail.com')
    SUPERUSER_FIRST_NAME = os.getenv('SUPERUSER_FIRST_NAME', 'Pavel')
    SUPERUSER_LAST_NAME = os.getenv('SUPERUSER_LAST_NAME', 'Miroshnichenko')

    SERVER_HOST = os.getenv('SERVER_HOST', '127.0.0.1')
    SERVER_PORT = int(os.getenv('SERVER_PORT', 5006))

    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:4200"]

    DB_SCHEME = os.getenv('DB_SCHEME')
    DB_HOST = os.getenv('POSTGRES_HOST')
    DB_PORT = os.getenv('POSTGRES_PORT')
    DB_USER = os.getenv('POSTGRES_USER')
    DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
    DB_NAME = os.getenv('POSTGRES_DB')
    DATABASE_URL: str = os.getenv(
        'DATABASE_URL', f'{DB_SCHEME}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

    HTTP_PROXY_HOST: str = os.getenv('HTTP_PROXY_HOST', None)
    HTTP_PROXY_PORT: int = int(os.getenv('HTTP_PROXY_PORT', None))
    HTTPS_PROXY_HOST: str = os.getenv('HTTPS_PROXY_HOST', None)
    HTTPS_PROXY_PORT: int = int(os.getenv('HTTPS_PROXY_PORT', None))

    BASE_URL: AnyHttpUrl = os.getenv('BASE_URL')
    KEYCLOAK_BASE_URL = os.getenv('KEYCLOAK_BASE_URL', 'localhost:8080/auth')

    KEYCLOAK_CLIENT_ID_ADMIN = os.getenv('KEYCLOAK_CLIENT_ID_ADMIN', 'admin-cli')
    KEYCLOAK_REALM_ADMIN = os.getenv('KEYCLOAK_REALM_ADMIN', 'master')
    KEYCLOAK_USERNAME_ADMIN = os.getenv('KEYCLOAK_USERNAME_ADMIN', 'admin')
    KEYCLOAK_PASSWORD_ADMIN = os.getenv('KEYCLOAK_PASSWORD_ADMIN', 'admin')
    KEYCLOAK_CLIENT_SECRET_ADMIN = os.getenv('KEYCLOAK_CLIENT_SECRET_ADMIN', '')

    KEYCLOAK_CLIENT_ID_APP = os.getenv('KEYCLOAK_CLIENT_ID_APP', 'master')
    KEYCLOAK_REALM_APP = os.getenv('KEYCLOAK_REALM_APP', 'master')

    SMTP_HOST: str = os.getenv('SMTP_HOST', 'localhost')
    SMTP_PORT: int = os.getenv('SMTP_HOST', 25)
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr = os.getenv('EMAILS_FROM_EMAIL')
    EMAILS_FROM_NAME: str | None = None

    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')
    CELERY_TIMEZONE = os.getenv('CELERY_TIMEZONE', 'Europe/Moscow')
    CELERY_BEAT_SCHEDULE = {
        'check_links_all': {
            'task': 'check_links_all',
            'schedule': crontab(hour=1, minute=0, day_of_week='1,2,3,4,5,6,0'),
        },
        'notify_users': {
            'task': 'notify_users_all',
            'schedule': crontab(hour=9, minute=0, day_of_week='1,2,3,4,5'),
        },
        'postgres_backup': {
            'task': 'postgres_backup',
            'schedule': crontab(hour=8, minute=30, day_of_week='1,2,3,4,5,6,0'),
        }
    }

    PROXY_LIST = OrderedDict(
        {
            'Country': (HTTP_PROXY_HOST, HTTP_PROXY_PORT),
        }
    )

    LOOP_LINK_CHUNK_SIZE = 500
    PLAYWRIGHT_LINK_CHUNK_SIZE = 5

settings = Settings()
