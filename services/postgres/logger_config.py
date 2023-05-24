import logging
from pathlib import Path

SERVICE_DIR = Path(__file__).resolve().parent
name = 'postgres'

logger = logging.getLogger(name=name)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s ")
file_handler = logging.FileHandler(SERVICE_DIR / f'{name}.log', encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
