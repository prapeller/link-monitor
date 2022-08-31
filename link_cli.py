import argparse
import asyncio
import os
import traceback
from datetime import datetime

from database import SessionLocal
from database.crud import get
from database.models.link import LinkModel
from database.models.user import UserModel
from services.link_checker import check_links

parser = argparse.ArgumentParser()
parser.add_argument('-uid', '--uid', type=int)
parser.add_argument('-id', '--id', type=int)
parser.add_argument('-l', '--list', nargs='+', type=int)
parser.add_argument('-a', '--all', action='store_const', const=True, default=False)
namespace = parser.parse_args()

try:
    db = SessionLocal()
    pid = os.getpid()

    start_time = datetime.now()
    print(f'Running link_cli on process {pid}, with namespace: {namespace}...')

    if namespace.uid:
        current_user = get(db, UserModel, id=namespace.uid)

    if namespace.id:
        # check one by id
        id = namespace.id
        link = get(db, LinkModel, id=id)
        if link:
            asyncio.run(check_links(db=db, links=[link]))
        else:
            print(f'no link with id={id} to check')

    elif namespace.list:
        # check from list
        links = db.query(LinkModel).filter(LinkModel.id.in_(namespace.list)).all()
        if links:
            asyncio.run(check_links(db=db, links=links))
        else:
            print('no links to check')

    elif namespace.all:
        # check all
        links = db.query(LinkModel).all()
        if links:
            asyncio.run(check_links(db=db, links=links))
        else:
            print('no links to check')

    finish_time = datetime.now()
    print(f'Exiting link_cli... executing time: {finish_time - start_time}')
    os.kill(pid, 9)

except Exception as e:
    print(traceback.format_exc())
