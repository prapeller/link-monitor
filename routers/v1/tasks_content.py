from datetime import datetime

import fastapi as fa

from core.dependencies import (
    get_current_user_dependency,
    get_sqlalchemy_repo_dependency,
)
from core.enums import TaskContentStatusEnum
from core.exceptions import UnauthorizedException
from core.languages import LANGUAGES_DICT
from core.shared import auth_head, auth_head_or_content_head
from database.models.task import TaskContentModel
from database.models.user import UserModel
from database.repository import SqlAlchemyRepository
from database.schemas.task import (
    TaskContentReadSerializer,
    TaskContentCreateSerializer,
    TaskContentUpdateSerializer,
    TaskContentReadUsersSerializer
)

router = fa.APIRouter()


@router.get(
    "/all",
    response_model=list[TaskContentReadUsersSerializer],
    status_code=fa.status.HTTP_200_OK,
)
@auth_head_or_content_head
async def tasks_content_list_all(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
):
    """
    to show content tasks in "all tasks" tab
    for current user (content_head)
    """
    tasks = repo.get_all(TaskContentModel)
    return tasks


@router.get(
    "/all/sent-to-content-teamlead",
    response_model=list[TaskContentReadUsersSerializer],
    status_code=fa.status.HTTP_200_OK,
)
@auth_head_or_content_head
async def tasks_content_list_all_sent_to_content_teamlead(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
):
    """
    to show content tasks in "Sent To Teamlead" tab
    for current user (content_head)
    """
    return repo.get_many(TaskContentModel, status=TaskContentStatusEnum.sent_to_teamlead)


@router.get(
    "/all/sent-to-content-author",
    response_model=list[TaskContentReadUsersSerializer],
    status_code=fa.status.HTTP_200_OK,
)
@auth_head_or_content_head
async def tasks_content_list_all_sent_to_content_author(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
):
    """
    to show content tasks in "Sent To Author" tab
    for current user (content_head)
    """
    return repo.get_many(TaskContentModel, status=TaskContentStatusEnum.sent_to_author)


@router.get(
    "/all/text-written",
    response_model=list[TaskContentReadUsersSerializer],
    status_code=fa.status.HTTP_200_OK,
)
@auth_head_or_content_head
async def tasks_content_list_all_text_written(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
):
    """
    to show content tasks in "Text Written" tab
    for current user (content_head)
    """
    return repo.get_many(TaskContentModel, status=TaskContentStatusEnum.text_written)


@router.get(
    "/all/in-edit",
    response_model=list[TaskContentReadUsersSerializer],
    status_code=fa.status.HTTP_200_OK,
)
@auth_head_or_content_head
async def tasks_content_list_all_in_edit(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
):
    """
    to show content tasks in "In Edit" tab
    for current user (content_head)
    """
    return repo.get_many(TaskContentModel, status=TaskContentStatusEnum.in_edit)


@router.get(
    "/all/closed",
    response_model=list[TaskContentReadUsersSerializer],
    status_code=fa.status.HTTP_200_OK,
)
@auth_head_or_content_head
async def tasks_content_list_all_closed(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
):
    """
    to show content tasks in "Closed" tab
    for current user (content_head)
    """
    return repo.get_many(TaskContentModel, status=TaskContentStatusEnum.closed)


@router.get(
    "/all/sent-to-webmaster",
    response_model=list[TaskContentReadUsersSerializer],
    status_code=fa.status.HTTP_200_OK,
)
@auth_head_or_content_head
async def tasks_content_list_all_sent_to_webmaster(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
):
    """
    to show content tasks in "Sent To WM" tab
    for current user (content_head)
    """
    return repo.get_many(TaskContentModel, status=TaskContentStatusEnum.sent_to_webmaster)


@router.get(
    "/my",
    response_model=list[TaskContentReadUsersSerializer],
    status_code=fa.status.HTTP_200_OK,
)
async def tasks_content_list_my(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
):
    """
    to show content tasks in "all tasks" tab
    for current user (content_teamlead/content_author/linker)
    """
    if current_user.is_content_teamlead:
        tasks = repo.get_many(TaskContentModel, content_teamlead_id=current_user.id)
    elif current_user.is_content_author:
        tasks = repo.get_many(TaskContentModel, content_author_id=current_user.id)
    else:
        tasks = repo.get_many(TaskContentModel, content_linkbuilder_id=current_user.id)
    return tasks


@router.get(
    "/my/sent-to-content-teamlead",
    response_model=list[TaskContentReadUsersSerializer],
    status_code=fa.status.HTTP_200_OK,
)
async def tasks_content_list_my_sent_to_content_teamlead(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
):
    """
    to show content tasks in "Sent To Teamlead" tab
    for current user (content_teamlead/linker)
    """
    if current_user.is_content_author:
        raise UnauthorizedException
    if current_user.is_content_teamlead:
        tasks_query = repo.get_query(TaskContentModel, content_teamlead_id=current_user.id)
    else:
        tasks_query = repo.get_query(TaskContentModel, content_linkbuilder_id=current_user.id)

    tasks = tasks_query.filter(
        TaskContentModel.status == TaskContentStatusEnum.sent_to_teamlead).all()
    return tasks


@router.get(
    "/my/sent-to-content-author",
    response_model=list[TaskContentReadUsersSerializer],
    status_code=fa.status.HTTP_200_OK,
)
async def tasks_content_list_my_sent_to_content_author(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
):
    """
    to show content tasks in "Sent To Author" tab
    for current user (content_teamlead/content_author/linker)
    """
    if current_user.is_content_teamlead:
        tasks_query = repo.get_query(TaskContentModel, content_teamlead_id=current_user.id)
    elif current_user.is_content_author:
        tasks_query = repo.get_query(TaskContentModel, content_author_id=current_user.id)
    else:
        tasks_query = repo.get_query(TaskContentModel, content_linkbuilder_id=current_user.id)

    tasks = tasks_query.filter(
        TaskContentModel.status == TaskContentStatusEnum.sent_to_author).all()
    return tasks


@router.get(
    "/my/text-written",
    response_model=list[TaskContentReadUsersSerializer],
    status_code=fa.status.HTTP_200_OK,
)
async def tasks_content_list_my_text_written(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
):
    """
    to show content tasks in "Text Written" tab
    for current user (content_teamlead/content_author/linker)
    """
    if current_user.is_content_teamlead:
        tasks_query = repo.get_query(TaskContentModel, content_teamlead_id=current_user.id)
    elif current_user.is_content_author:
        tasks_query = repo.get_query(TaskContentModel, content_author_id=current_user.id)
    else:
        tasks_query = repo.get_query(TaskContentModel, content_linkbuilder_id=current_user.id)

    tasks = tasks_query.filter(
        TaskContentModel.status == TaskContentStatusEnum.text_written).all()
    return tasks


@router.get(
    "/my/in-edit",
    response_model=list[TaskContentReadUsersSerializer],
    status_code=fa.status.HTTP_200_OK,
)
async def tasks_content_list_my_in_edit(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
):
    """
    to show content tasks in "In Edit" tab
    for current user (content_teamlead/content_author/linker)
    """
    if current_user.is_content_teamlead:
        tasks_query = repo.get_query(TaskContentModel, content_teamlead_id=current_user.id)
    elif current_user.is_content_author:
        tasks_query = repo.get_query(TaskContentModel, content_author_id=current_user.id)
    else:
        tasks_query = repo.get_query(TaskContentModel, content_linkbuilder_id=current_user.id)

    tasks = tasks_query.filter(
        TaskContentModel.status == TaskContentStatusEnum.in_edit).all()
    return tasks


@router.get(
    "/my/closed",
    response_model=list[TaskContentReadUsersSerializer],
    status_code=fa.status.HTTP_200_OK,
)
async def tasks_content_list_my_closed(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
):
    """
    to show content tasks in "Closed" tab
    for current user (content_teamlead/content_author/linker)
    """
    if current_user.is_content_teamlead:
        tasks_query = repo.get_query(TaskContentModel, content_teamlead_id=current_user.id)
    elif current_user.is_content_author:
        tasks_query = repo.get_query(TaskContentModel, content_author_id=current_user.id)
    else:
        tasks_query = repo.get_query(TaskContentModel, content_linkbuilder_id=current_user.id)

    tasks = tasks_query.filter(
        TaskContentModel.status == TaskContentStatusEnum.closed).all()
    return tasks


@router.get(
    "/my/sent-to-webmaster",
    response_model=list[TaskContentReadUsersSerializer],
    status_code=fa.status.HTTP_200_OK,
)
async def tasks_content_list_my_sent_to_webmaster(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
):
    """
    to show content tasks in "Sent To WM" tab
    for current user (content_teamlead/content_author/linker)
    """
    if current_user.is_content_teamlead:
        tasks_query = repo.get_query(TaskContentModel, content_teamlead_id=current_user.id)
    elif current_user.is_content_author:
        tasks_query = repo.get_query(TaskContentModel, content_author_id=current_user.id)
    else:
        tasks_query = repo.get_query(TaskContentModel, content_linkbuilder_id=current_user.id)

    tasks = tasks_query.filter(
        TaskContentModel.status == TaskContentStatusEnum.sent_to_webmaster).all()
    return tasks


@router.get(
    "/{task_id}",
    response_model=TaskContentReadUsersSerializer,
    status_code=fa.status.HTTP_200_OK,
)
@auth_head
async def tasks_content_get(
        task_id: int,
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
):
    """
    get content task by id
    """
    task = repo.get(TaskContentModel, id=task_id)

    return task


@router.get(
    "/languages/all",
    status_code=fa.status.HTTP_200_OK,
)
async def tasks_content_get_languages():
    """
    get languages dict
    """
    return LANGUAGES_DICT


@router.put(
    "/{task_id}",
    response_model=TaskContentReadUsersSerializer,
    status_code=fa.status.HTTP_202_ACCEPTED,
)
async def task_content_update(
        task_id: int,
        task_content_ser: TaskContentUpdateSerializer,
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
):
    """
    update task by id,
    if status=='closed', then set .closed_at
    """
    if task_content_ser.status == TaskContentStatusEnum.closed:
        task_content_ser.closed_at = datetime.now()
    task_content = repo.get(TaskContentModel, id=task_id)
    task_content = repo.update(task_content, task_content_ser)
    return task_content


@router.post(
    "/",
    response_model=TaskContentReadSerializer,
)
async def task_content_create(
        task_content_ser: TaskContentCreateSerializer,
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
):
    """
    create task by linkbuilder, set task.content_teamlead_viewed=False, set deadline
    """
    task_content = task_content_ser.create(repo, current_user)
    return task_content


@router.delete(
    "/{task_id}",
)
async def task_content_delete(
        task_id: int,
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
):
    """
    remove task by id
    """
    task_content = repo.get(TaskContentModel, id=task_id)
    if task_content is None:
        raise fa.HTTPException(status_code=404, detail="task not found")

    repo.remove(TaskContentModel, id=task_id)
    return {'message': 'ok'}
