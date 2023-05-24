import os
import subprocess

from celery_app import celery_app
from core.enums import EnvEnum
from services.postgres.logger_config import logger


@celery_app.task(name='postgres_backup')
def postgres_backup():
    script_path = f"{os.getcwd()}/scripts/postgres/dump.sh"
    subprocess.run(script_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={'ENV': EnvEnum.prod})
    logger.info(f'postgres_backup task')
