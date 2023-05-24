from celery_app import celery_app
from database import SessionLocal
from database.repository import SqlAlchemyRepository
from services.reporter import logger


@celery_app.task(name='check_if_content_data_created_on_tasks_all')
def check_if_content_data_created_on_tasks_all() -> str:
    logger.debug('check_if_content_data_created_on_tasks_all')
    repo = SqlAlchemyRepository(SessionLocal())
    results = repo.check_if_content_data_created_on_tasks_all()
    repo.session.close()
    return str(results)


@celery_app.task(name='check_if_content_data_created_on_tasks_by_ids')
def check_if_content_data_created_on_tasks_by_ids(id_list: list[int]) -> str:
    logger.debug('check_if_content_data_created_on_tasks_by_ids')
    repo = SqlAlchemyRepository(SessionLocal())
    results = repo.check_if_content_data_created_on_tasks_by_ids(id_list)
    repo.session.close()
    return str(results)
