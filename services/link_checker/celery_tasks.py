import asyncio
import datetime

from sqlalchemy import extract

from celery_app import celery_app
from core.config import settings
from core.shared import chunks_generator
from database import SessionLocal
from database.crud import get
from database.models import init_models
from database.models.link import LinkModel
from services.link_checker.link_checker import LinkChecker, logger


@celery_app.task(name='check_link_by_id')
def check_link_by_id(id):
    init_models()
    session = SessionLocal()
    link = get(session, LinkModel, id=id)
    if link:
        logger.debug('check_link_by_id task')
        linkchecker = LinkChecker(session)
        asyncio.run(linkchecker.check_links(links=[link]))
    else:
        logger.error(f'check_link_by_id task: no link with id={id} was found to check')
    session.close()


@celery_app.task(name='check_links_from_list')
def check_links_from_list(id_list):
    init_models()
    session = SessionLocal()
    links = session.query(LinkModel).filter(LinkModel.id.in_(id_list)).all()
    if links:
        for link_chunk in chunks_generator(links, settings.LINK_CHECKER_CHUNK_SIZE):
            logger.debug(f'check_links_from_list task, LINK_CHECKER_CHUNK_SIZE: {settings.LINK_CHECKER_CHUNK_SIZE}')
            linkchecker = LinkChecker(session)
            asyncio.run(linkchecker.check_links(links=link_chunk))
    else:
        logger.error('check_links_from_list task: no links in db was found to check')
    session.close()


@celery_app.task(name='check_links_all')
def check_links_all():
    init_models()
    session = SessionLocal()
    links = session.query(LinkModel).all()
    if links:
        for link_chunk in chunks_generator(links, settings.LINK_CHECKER_CHUNK_SIZE):
            logger.debug(f'check_links_all task, LINK_CHECKER_CHUNK_SIZE: {settings.LINK_CHECKER_CHUNK_SIZE}')
            linkchecker = LinkChecker(session)
            asyncio.run(linkchecker.check_links(links=link_chunk))
    else:
        logger.error('check_links_all task: no links in db was found to check')
    session.close()


@celery_app.task(name='check_every_day')
def check_every_day():
    """
    mode httpx(None): all
    mode playwright: status red
    """
    init_models()
    session = SessionLocal()

    links_httpx_mode = session.query(LinkModel) \
        .filter(LinkModel.link_check_last_check_mode == None).all()
    links_playwright_mode = session.query(LinkModel) \
        .filter(LinkModel.link_check_last_check_mode == 'playwright') \
        .filter(LinkModel.link_check_last_status == 'red') \
        .all()
    links = links_httpx_mode + links_playwright_mode
    if links:
        for link_chunk in chunks_generator(links, settings.LINK_CHECKER_CHUNK_SIZE):
            logger.debug(f'check_every_day task: LINK_CHECKER_CHUNK_SIZE: {settings.LINK_CHECKER_CHUNK_SIZE}')
            linkchecker = LinkChecker(session)
            asyncio.run(linkchecker.check_links(links=link_chunk))
    else:
        logger.error('check_every_day task: no links in db was found to check')
    session.close()


@celery_app.task(name='check_monthly')
def check_monthly():
    """
    mode playwright: status green and link.link_check_last_created_at <= settings.OLD_LINKCHECKS_DAYS
    """
    init_models()
    session = SessionLocal()
    old_links_date = datetime.datetime.now() - datetime.timedelta(days=settings.OLD_LINKCHECKS_DAYS)

    links = session.query(LinkModel) \
        .filter(LinkModel.link_check_last_status == 'green') \
        .filter(LinkModel.link_check_last_created_at <= old_links_date) \
        .all()
    if links:
        for link_chunk in chunks_generator(links, settings.LINK_CHECKER_CHUNK_SIZE):
            logger.debug(f'check_monthly task: LINK_CHECKER_CHUNK_SIZE: {settings.LINK_CHECKER_CHUNK_SIZE}')
            linkchecker = LinkChecker(session, start_mode='playwright')
            asyncio.run(linkchecker.check_links(links=link_chunk))
    else:
        logger.error('check_monthly task: no links in db was found to check')
    session.close()


@celery_app.task(name='check_links_from_list_playwright')
def check_links_from_list_playwright(id_list):
    init_models()
    session = SessionLocal()
    links = session.query(LinkModel).filter(LinkModel.id.in_(id_list)).all()
    if links:
        for link_chunk in chunks_generator(links, settings.LINK_CHECKER_CHUNK_SIZE):
            logger.debug(
                f'check_links_from_list_playwright task: LINK_CHECKER_CHUNK_SIZE: {settings.LINK_CHECKER_CHUNK_SIZE}')
            linkchecker = LinkChecker(session, start_mode='playwright')
            asyncio.run(linkchecker.check_links(links=link_chunk))
    else:
        logger.error('check_links_from_list_playwright task: no links in db was found to check')
    session.close()


@celery_app.task(name='check_links_per_year')
def check_links_per_year(year: int):
    init_models()
    session = SessionLocal()
    links = session.query(LinkModel).filter(extract('year', LinkModel.created_at) == year).all()
    if links:
        for link_chunk in chunks_generator(links, settings.LINK_CHECKER_CHUNK_SIZE):
            logger.debug(f'check_links_per_year task: LINK_CHECKER_CHUNK_SIZE: {settings.LINK_CHECKER_CHUNK_SIZE}')
            linkchecker = LinkChecker(session)
            asyncio.run(linkchecker.check_links(links=link_chunk))
    else:
        logger.error('check_links_per_year task: no links in db was found to check')
    session.close()
