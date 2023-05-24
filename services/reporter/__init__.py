import logging

logger = logging.getLogger(name='reporter')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s ")
file_handler = logging.FileHandler(f'services/reporter/reporter.log', encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
