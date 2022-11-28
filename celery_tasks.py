import asyncio
import os
import subprocess

from sqlalchemy import extract
from celery_app import celery_app

from core.config import settings
from core.exceptions import WhileUploadingArchiveException
from core.shared import chunks_generator, set_link_check_last
from database import SessionLocal
from database.crud import get, create, get_or_create_many_links_from_archive
from database.models import init_models
from database.models.link import LinkModel
from database.models.user import UserModel
from database.repository import SqlAlchemyRepository
from database.schemas.user import UserCreateSerializer
from services.domain_checker import recreate_domains
from services.file_handler import check_file_on_duplicates, get_link_create_ser_list_from_file
from services.keycloak import KCAdmin
from services.link_checker import LinkChecker
from services.notificator import notify_users


@celery_app.task(name='check_link_by_id')
def check_link_by_id(id):
    init_models()
    session = SessionLocal()
    link = get(session, LinkModel, id=id)
    if link:
        linkchecker = LinkChecker(session)
        print(linkchecker)
        asyncio.run(linkchecker.check_links(links=[link]))
        print(f'LOOP_LINK_CHUNK_SIZE: {settings.LOOP_LINK_CHUNK_SIZE}\n\n\n')
    else:
        print(f'no link with id={id} to check')
    session.close()


@celery_app.task(name='check_links_from_list')
def check_links_from_list(id_list):
    init_models()
    session = SessionLocal()
    links = session.query(LinkModel).filter(LinkModel.id.in_(id_list)).all()
    if links:
        for link_chunk in chunks_generator(links, settings.LOOP_LINK_CHUNK_SIZE):
            linkchecker = LinkChecker(session)
            print(linkchecker)
            asyncio.run(linkchecker.check_links(links=link_chunk))
            print(f'LOOP_LINK_CHUNK_SIZE: {settings.LOOP_LINK_CHUNK_SIZE}\n\n\n')
    else:
        print('no links to check')
    session.close()


@celery_app.task(name='check_links_all')
def check_links_all():
    init_models()
    session = SessionLocal()
    links = session.query(LinkModel).all()
    if links:
        for link_chunk in chunks_generator(links, settings.LOOP_LINK_CHUNK_SIZE):
            linkchecker = LinkChecker(session)
            print(linkchecker)
            asyncio.run(linkchecker.check_links(links=link_chunk))
            print(f'LOOP_LINK_CHUNK_SIZE: {settings.LOOP_LINK_CHUNK_SIZE}\n\n\n')
    else:
        print('no links to check')
    session.close()


@celery_app.task(name='check_links_from_list_playwright')
def check_links_from_list_playwright(id_list):
    init_models()
    session = SessionLocal()
    links = session.query(LinkModel).filter(LinkModel.id.in_(id_list)).all()
    if links:
        for link_chunk in chunks_generator(links, settings.LOOP_LINK_CHUNK_SIZE):
            linkchecker = LinkChecker(session, start_mode='playwright')
            print(linkchecker)
            asyncio.run(linkchecker.check_links(links=link_chunk))
            print(f'LOOP_LINK_CHUNK_SIZE: {settings.LOOP_LINK_CHUNK_SIZE}\n\n\n')
    else:
        print('no links to check')
    session.close()


@celery_app.task(name='check_links_per_year')
def check_links_per_year(year: int):
    init_models()
    session = SessionLocal()
    links = session.query(LinkModel).filter(extract('year', LinkModel.created_at) == year).all()
    if links:
        for link_chunk in chunks_generator(links, settings.LOOP_LINK_CHUNK_SIZE):
            linkchecker = LinkChecker(session)
            print(linkchecker)
            asyncio.run(linkchecker.check_links(links=link_chunk))
            print(f'LOOP_LINK_CHUNK_SIZE: {settings.LOOP_LINK_CHUNK_SIZE}\n\n\n')
    else:
        print('no links to check')
    session.close()


@celery_app.task(name='notify_users_all')
def notify_users_all():
    init_models()
    session = SessionLocal()
    users = session.query(UserModel).all()
    notify_users(session, users)
    session.close()


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


@celery_app.task(name='create_links_from_uploaded_file_archive')
def create_links_from_uploaded_file_archive(uploaded_file_path, current_user_id):
    init_models()
    session = SessionLocal()
    current_user = get(session, UserModel, id=current_user_id)
    duplicate_validation_errors = check_file_on_duplicates(filepath=uploaded_file_path)
    if duplicate_validation_errors:
        raise WhileUploadingArchiveException(message='duplicates in archive were found',
                                             errors=duplicate_validation_errors,
                                             user=current_user)
    link_create_ser_list = get_link_create_ser_list_from_file(filepath=uploaded_file_path,
                                                              current_user_id=current_user.id,
                                                              mode='from_archive')
    links = get_or_create_many_links_from_archive(session, link_create_ser_list)
    links_id_list = [str(link.id) for link in links]
    check_links_from_list.delay(id_list=links_id_list)
    session.close()


@celery_app.task(name='set_link_check_last_ids')
def set_link_check_last_ids(id_list):
    init_models()
    session = SessionLocal()
    links = session.query(LinkModel).filter(LinkModel.id.in_(id_list)).all()
    for link in links:
        set_link_check_last(link)
    session.commit()
    session.close()


@celery_app.task(name='postgres_backup')
def postgres_backup():
    script_path = f"{os.getcwd()}/scripts/postgres/backup.sh"
    subprocess.run(script_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


@celery_app.task(name='recreate_domains_task')
def recreate_domains_task():
    session = SessionLocal()
    repo = SqlAlchemyRepository(session)
    links = repo.get_all(LinkModel)
    for link in sorted(links, key=lambda x: x.id):
        recreate_domains(session, link)
    session.close()