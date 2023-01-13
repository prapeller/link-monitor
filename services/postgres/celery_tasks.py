import logging
import os
import subprocess

from celery_app import celery_app


logger = logging.getLogger(name='postgres')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s ")
file_handler = logging.FileHandler(f'services/postgres/postgres.log', encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


@celery_app.task(name='postgres_backup')
def postgres_backup():
    script_path = f"{os.getcwd()}/scripts/postgres/backup.sh"
    subprocess.run(script_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logger.info(f'postgres_backup task')
