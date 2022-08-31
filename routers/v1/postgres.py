import os
import subprocess

import fastapi as fa
from fastapi import UploadFile
from fastapi.responses import FileResponse

from core.dependencies import get_current_user_dependency
from core.exceptions import UnauthorizedException
from database.models.user import UserModel

router = fa.APIRouter()


@router.post("/dump", status_code=fa.status.HTTP_201_CREATED)
async def postgres_dump(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        from_local: bool = False
):
    if not current_user.is_head:
        raise UnauthorizedException
    script_path = f"{os.getcwd()}/scripts/postgres/backup_local.sh" if from_local else f"{os.getcwd()}/scripts/postgres/backup.sh"
    assert os.path.isfile(script_path)
    result = subprocess.run(script_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return {
        'stderr': f'{result.stderr.decode("utf-8", "ignore")}',
        'stdout': f'{result.stdout.decode("utf-8", "ignore")}',
    }


@router.get("/check-dumps")
async def postgres_check_dumps(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    if not current_user.is_head:
        raise UnauthorizedException
    script_path = f"{os.getcwd()}/scripts/postgres/backups.sh"
    assert os.path.isfile(script_path)
    result = subprocess.run(script_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return {
        'stderr': f'{result.stderr.decode("utf-8", "ignore")}',
        'stdout': f'{result.stdout.decode("utf-8", "ignore")}',
    }


@router.get("/download-last-dump")
async def postgres_download_last_dump(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    if not current_user.is_head:
        raise UnauthorizedException
    file_path = f"{os.getcwd()}/static/backups/backup_last"
    assert os.path.isfile(file_path)
    headers = {'Content-Disposition': 'attachment',
               'Content-Type': 'application/octet-stream'}
    return FileResponse(path=file_path, headers=headers, filename='backup_last')


@router.post("/restore", status_code=fa.status.HTTP_201_CREATED)
async def postgres_restore(
        dump_file: UploadFile,
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        from_local: bool = False
):
    if not current_user.is_head:
        raise UnauthorizedException
    contents = await dump_file.read()
    uploaded_file_path = f'static/backups/uploaded_backup'
    with open(uploaded_file_path, 'wb') as uploaded:
        uploaded.write(contents)

    script_path = f"{os.getcwd()}/scripts/postgres/restore_local.sh" if from_local else f"{os.getcwd()}/scripts/postgres/restore.sh"
    subprocess.Popen(script_path)
    return {'message': 'ok'}
