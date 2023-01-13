import asyncio

from celery_app import celery_app
from database.models import init_models
from services.domain_checker.domain_checker import PageUrlDomainChecker, logger


@celery_app.task(name='check_pudomains_with_similarweb')
def check_pudomains_with_similarweb(id_list):
    init_models()
    if id_list:
        logger.debug('check_pudomains_with_similarweb task')
        pudomain_checker = PageUrlDomainChecker(pudomain_id_list=id_list)
        asyncio.run(pudomain_checker.run_check())
    else:
        logger.debug(f'no pudomain_id_list was passed')
