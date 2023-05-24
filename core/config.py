import os
import secrets
from collections import OrderedDict
from pathlib import Path
from typing import List

from celery.schedules import crontab
from pydantic import BaseSettings, AnyHttpUrl, EmailStr


class Settings(BaseSettings):
    BASE_DIR = Path(__file__).resolve().parent.parent
    from dotenv import load_dotenv
    DEBUG = True if os.getenv('DEBUG', 'False') == 'True' else False
    DOCKER_COMPOSE = True if os.getenv('DOCKER_COMPOSE', 'False') == 'True' else False
    if DEBUG and DOCKER_COMPOSE:
        load_dotenv(BASE_DIR / '.envs/.docker-compose-local')
    elif DEBUG and not DOCKER_COMPOSE:
        load_dotenv(BASE_DIR / '.envs/.local')
    else:
        load_dotenv(BASE_DIR / '.envs/.prod')

    SECRET_KEY: str = secrets.token_urlsafe(32)

    SUPERUSER_EMAIL = os.getenv('SUPERUSER_EMAIL', 'pavelmirosh@gmail.com')
    SUPERUSER_FIRST_NAME = os.getenv('SUPERUSER_FIRST_NAME', 'Pavel')
    SUPERUSER_LAST_NAME = os.getenv('SUPERUSER_LAST_NAME', 'Mirosh')

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

    HTTP_PROXY: str = os.getenv('HTTP_PROXY', None)
    HTTPS_PROXY: str = os.getenv('HTTPS_PROXY', None)

    BASE_URL: AnyHttpUrl = os.getenv('BASE_URL', 'https://report.kaisaco.com')
    KEYCLOAK_BASE_URL = os.getenv('KEYCLOAK_BASE_URL', 'localhost:8080/auth')

    KEYCLOAK_CLIENT_ID_ADMIN = os.getenv('KEYCLOAK_CLIENT_ID_ADMIN', 'admin-cli')
    KEYCLOAK_REALM_ADMIN = os.getenv('KEYCLOAK_REALM_ADMIN', 'master')
    KEYCLOAK_USERNAME_ADMIN = os.getenv('KEYCLOAK_USERNAME_ADMIN', 'admin')
    KEYCLOAK_PASSWORD_ADMIN = os.getenv('KEYCLOAK_PASSWORD_ADMIN', 'admin')
    KEYCLOAK_CLIENT_SECRET_ADMIN = os.getenv('KEYCLOAK_CLIENT_SECRET_ADMIN', '')

    KEYCLOAK_CLIENT_ID_APP = os.getenv('KEYCLOAK_CLIENT_ID_REPORT', 'report')
    KEYCLOAK_REALM_APP = os.getenv('KEYCLOAK_REALM_REPORT', 'report')

    SMTP_HOST: str = os.getenv('SMTP_HOST', 'kaisaco.com')
    SMTP_PORT: int = os.getenv('SMTP_HOST', 25)
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr = os.getenv('EMAILS_FROM_EMAIL', 'report@kaisaco.com')
    EMAILS_FROM_NAME: str | None = None

    TG_BOT_ID: str = 'bot...'

    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')
    CELERY_TIMEZONE = os.getenv('CELERY_TIMEZONE', 'Europe/Moscow')
    CELERY_BEAT_SCHEDULE = {
        'check_every_day': {
            'task': 'check_every_day',
            'schedule': crontab(hour=1, minute=0, day_of_week='1,2,3,4,5,6,0'),
        },
        'check_monthly': {
            'task': 'check_monthly',
            'schedule': crontab(hour=5, minute=0, day_of_month='1'),
        },
        'prepare_and_send_linkers_report_daily_messages': {
            'task': 'prepare_and_send_linkers_report_daily_messages',
            'schedule': crontab(minute=0, day_of_week='1,2,3,4,5'),
        },
        'prepare_and_send_content_author_todo_messages': {
            'task': 'prepare_and_send_content_author_todo_messages',
            'schedule': crontab(minute=0, day_of_week='1,2,3,4,5'),
        },
        'prepare_and_send_content_author_changed_to_edit_messages': {
            'task': 'prepare_and_send_content_author_changed_to_edit_messages',
            'schedule': crontab(minute=0, day_of_week='1,2,3,4,5'),
        },
        'prepare_and_send_content_author_deadline_overdue_messages': {
            'task': 'prepare_and_send_content_author_deadline_overdue_messages',
            'schedule': crontab(minute=0, day_of_week='1,2,3,4,5,6,0'),
        },
        'prepare_and_send_content_author_and_teamlead_are_idle_messages': {
            'task': 'prepare_and_send_content_author_and_teamlead_are_idle_messages',
            'schedule': crontab(minute=0, day_of_week='1,2,3,4,5'),
        },
        'postgres_backup': {
            'task': 'postgres_backup',
            'schedule': crontab(hour=8, minute=30, day_of_week='1,2,3,4,5,6,0'),
        }
    }

    LINK_CHECKER_PROXY_ORDERED_DICT = OrderedDict(
        {
        }
    )
    DOMAIN_CHECKER_PROXY_ORDERED_DICT = OrderedDict(
        {
        }
    )

    LINK_CHECKER_CHUNK_SIZE = 100
    PLAYWRIGHT_LINK_CHUNK_SIZE = 5
    OLD_LINKCHECKS_DAYS = 30

    BUSINESS_DAYS_TO_ADD_SHORT = 3
    BUSINESS_DAYS_TO_ADD_LONG = 5

    CONTENT_AUTHOR_MONTH_WORDS_QTY_PLAN = 30000

    SSL_EXPIRATION_DAYS = 30

    NOTIFICATIONS_HOURS_CONTENT_AUTHORS_TODO = [7, 11, 15, 19]
    NOTIFICATIONS_HOURS_CONTENT_AUTHORS_INEDIT = [7, 9, 11, 13, 15, 17, 19, 21]
    NOTIFICATIONS_HOURS_CONTENT_AUTHORS_TODO_OVERDUE = [7]
    NOTIFICATIONS_HOURS_CONTENT_AUTHORS_TEAMLEADS_IDLE = [7]
    DAYS_CONTENT_AUTHORS_TEAMLEADS_IDLE_TO_NOTIFY = 2
    NOTIFICATIONS_HOURS_LINKERS_DAILY_REPORT = [9]


settings = Settings()
