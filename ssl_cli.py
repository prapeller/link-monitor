import argparse
import os
import subprocess
import time
from datetime import datetime

from database import SessionLocal
from database.crud import get
from database.models import init_models
from database.models.link import LinkModel
from database.models.link_check import LinkCheckModel
from services.ssl_checker.ssl_checker import get_ssl_expiration_date

parser = argparse.ArgumentParser()
parser.add_argument('-id', '--id', type=int)
parser.add_argument('-l', '--list', nargs='+', type=int)
parser.add_argument('-a', '--all', action='store_const', const=True, default=False)
namespace = parser.parse_args()
PARALLELPROC = 5

init_models()
db = SessionLocal()
pid = os.getpid()

if namespace.id:
    # check one by id
    linkcheck_id = namespace.id
    linkcheck = get(db, LinkCheckModel, id=linkcheck_id)
    page_url_domain_name = linkcheck.link.page_url_domain.name
    print(f'Started ssl_cli on process {pid}, with namespace: {namespace} for {page_url_domain_name}...')
    ssl_expiration_date = get_ssl_expiration_date(page_url_domain_name)

    linkcheck.ssl_expiration_date = ssl_expiration_date
    linkcheck.ssl_expires_in_days = (
            ssl_expiration_date - datetime.now()).days if ssl_expiration_date else -1
    db.commit()
    print(f'Finished ssl_cli on process {pid}, with namespace: {namespace} for {page_url_domain_name}...')
    os.kill(pid, 9)

elif namespace.list:
    # check many from list
    linkschecks_id_list = namespace.list
    print(f'Started ssl_cli on process {pid}, with namespace: {namespace} for linkchecks {linkschecks_id_list}...')
    process_list = []

    for linkcheck_id in linkschecks_id_list:
        p = subprocess.Popen(
            ["python3.10", "ssl_cli.py", "-id", str(linkcheck_id)],
        )

        process_list.append(p)
        while len(process_list) > PARALLELPROC:
            time.sleep(0.5)
            for p in process_list:
                if p.poll() is not None:
                    process_list.remove(p)
    print(f'Finished ssl_cli on process {pid}, with namespace: {namespace} for linkchecks {linkschecks_id_list}...')
    os.kill(pid, 9)

elif namespace.all:
    # check all
    link_list: list[LinkModel] = db.query(LinkModel).all()
    linkcheck_list = [link.link_check_last for link in link_list]
    linkchecks_id_list = [str(linkcheck.id) for linkcheck in linkcheck_list]
    print(f'Started ssl_cli on process {pid}, with namespace: {namespace} for linkchecks {linkchecks_id_list}...')
    process_list = []

    for linkcheck_id in linkchecks_id_list:
        p = subprocess.Popen(
            ["python3.10", "ssl_cli.py", "-id", str(linkcheck_id)],
        )

        process_list.append(p)
        while len(process_list) > PARALLELPROC:
            time.sleep(0.5)
            for p in process_list:
                if p.poll() is not None:
                    process_list.remove(p)
    print(f'Finished ssl_cli on process {pid}, with namespace: {namespace} for linkchecks {linkchecks_id_list}...')
    os.kill(pid, 9)
