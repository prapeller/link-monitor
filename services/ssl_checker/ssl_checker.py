import logging
import subprocess
import traceback
from datetime import datetime

from core.config import settings

logger = logging.getLogger(name='ssl_checker')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s ")
file_handler = logging.FileHandler(f'services/ssl_checker/ssl_checker.log', encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def get_ssl_expiration_date(hostname):
    date_fmt = r'%b %d %H:%M:%S %Y GMT'
    url = f'https://{hostname}'

    http_proxy = settings.HTTP_PROXY
    export_http_proxy_str = f'export http_proxy={http_proxy} && ' if http_proxy else ''
    https_proxy = settings.HTTPS_PROXY
    export_https_proxy_str = f'export http_proxy={https_proxy} && ' if https_proxy else ''
    try:
        date_str = subprocess.getoutput(
            f"{export_http_proxy_str}"
            f"{export_https_proxy_str}"
            f'curl {url} -m 5 -vI --stderr - | grep "expire date" | cut -d":" -f 2-'
        ).strip()

        ssl_expiration_date = datetime.strptime(date_str, date_fmt) if date_str else None
        return ssl_expiration_date

    except Exception:
        logger.error(traceback.format_exc())
        return None
