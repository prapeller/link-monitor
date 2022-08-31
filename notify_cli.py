import argparse
import os
import traceback
from datetime import datetime

from database import SessionLocal
from database.crud import get_query_all_active
from database.models.user import UserModel
from services.notificator import notify_user, notify_users

parser = argparse.ArgumentParser()
parser.add_argument('-id', '--id', type=int)
parser.add_argument('-l', '--list', nargs='+', type=int)
parser.add_argument('-a', '--all', action='store_const', const=True, default=False)
namespace = parser.parse_args()

try:
    db = SessionLocal()
    pid = os.getpid()

    start_time = datetime.now()
    print(f'Running notify_cli on process {pid}, with namespace: {namespace}...')

    if namespace.id:
        # notify one user by id
        id = namespace.id
        user = get_query_all_active(db, UserModel).filter_by(id=id).first()
        if user:
            notify_user(db=db, user=user)
        else:
            print(f"There's no active user with id={id} to notify!")

    elif namespace.list:
        # notify users from list
        users = get_query_all_active(db, UserModel).filter(UserModel.id.in_(namespace.list)).all()
        if users:
            notify_users(db=db, users=users)
        else:
            print(f"There's no active users with ids: {namespace.list} to notify!")

    elif namespace.all:
        # notify all users
        users = get_query_all_active(db, UserModel).all()
        if users:
            notify_users(db=db, users=users)
        else:
            print("There's no active users to notify!")

    finish_time = datetime.now()
    print(f'Exiting notify_cli... executing time: {finish_time - start_time}')
    os.kill(pid, 9)

except Exception as e:
    print(traceback.format_exc())
