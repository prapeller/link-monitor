from datetime import datetime

import fastapi as fa
from sqlalchemy.orm import Session

from core.dependencies import get_current_user_dependency, get_sqlalchemy_repo_dependency, get_session_dependency
from core.enums import TaskContentStatusEnum
from core.shared import auth_head_only
from database.models.task import TaskContentModel
from database.models.user import UserModel
from database.repository import SqlAlchemyRepository
from database.schemas.task import TaskContentReadSerializer, TaskContentCreateSerializer, TaskContentUpdateSerializer

router = fa.APIRouter()


@router.get(
    "/all",
    response_model=list[TaskContentReadSerializer],
    status_code=fa.status.HTTP_200_OK,
)
@auth_head_only
async def tasks_content_list_all(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
):
    """
    get all content tasks
    """
    tasks = repo.get_all(TaskContentModel)
    return tasks


@router.get(
    "/my",
    response_model=list[TaskContentReadSerializer],
    status_code=fa.status.HTTP_200_OK,
)
async def tasks_content_list_my(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
):
    """
    get content tasks for current user:
    if current user.is_content_teamlead - get all with task.content_teamlead_id=current_user.id,
    if current user.is_content_author - get all with task.content_author_id=current_user.id,
    if current user is none of above - get all tasks who created them, ie with task.content_linkbuilder_id=current_user.id
    """
    if current_user.is_content_teamlead:
        tasks = repo.get_many(TaskContentModel, content_teamlead_id=current_user.id)
    elif current_user.is_content_author:
        tasks = repo.get_many(TaskContentModel, content_author_id=current_user.id)
    else:
        tasks = repo.get_many(TaskContentModel, content_linkbuilder_id=current_user.id)
    return tasks


@router.get(
    "/my/in-progress",
    response_model=list[TaskContentReadSerializer],
    status_code=fa.status.HTTP_200_OK,
)
async def tasks_content_list_my_in_progress(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        session: Session = fa.Depends(get_session_dependency),
):
    """
    get content tasks for current user:
    if current user.is_content_teamlead - get all with                          task.content_teamlead_id=current_user.id    and task.status in (sent to teamlead/sent to author/text written/confirmed)
    if current user.is_content_author - get all with                            task.content_author_id=current_user.id      and task.status in (sent to teamlead/sent to author/text written/confirmed)
    if current user is none of above - get all tasks who created them, ie with  task.content_linkbuilder_id=current_user.id and task.status in (sent to teamlead/sent to author/text written/confirmed/in edit)
    """
    if current_user.is_content_teamlead:
        tasks = session.query(TaskContentModel) \
            .filter(TaskContentModel.content_teamlead_id == current_user.id) \
            .filter(TaskContentModel.status.in_(
            (TaskContentStatusEnum.sent_to_teamlead,
             TaskContentStatusEnum.sent_to_author,
             TaskContentStatusEnum.text_written,
             TaskContentStatusEnum.confirmed))) \
            .all()
    elif current_user.is_content_author:
        tasks = session.query(TaskContentModel) \
            .filter(TaskContentModel.content_author_id == current_user.id) \
            .filter(TaskContentModel.status.in_(
            (TaskContentStatusEnum.sent_to_teamlead,
             TaskContentStatusEnum.sent_to_author,
             TaskContentStatusEnum.text_written,
             TaskContentStatusEnum.confirmed))) \
            .all()
    else:
        tasks = session.query(TaskContentModel) \
            .filter(TaskContentModel.content_linkbuilder_id == current_user.id) \
            .filter(TaskContentModel.status.in_(
            (TaskContentStatusEnum.sent_to_teamlead,
             TaskContentStatusEnum.sent_to_author,
             TaskContentStatusEnum.text_written,
             TaskContentStatusEnum.confirmed,
             TaskContentStatusEnum.in_edit))) \
            .all()
    return tasks


@router.get(
    "/my/closed",
    response_model=list[TaskContentReadSerializer],
    status_code=fa.status.HTTP_200_OK,
)
async def tasks_content_list_my_closed(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        session: Session = fa.Depends(get_session_dependency),
):
    """
    get closed content tasks for current user"""
    if current_user.is_content_teamlead:
        tasks = session.query(TaskContentModel) \
            .filter(TaskContentModel.content_teamlead_id == current_user.id) \
            .filter(TaskContentModel.status == TaskContentStatusEnum.closed) \
            .all()
    elif current_user.is_content_author:
        tasks = session.query(TaskContentModel) \
            .filter(TaskContentModel.content_author_id == current_user.id) \
            .filter(TaskContentModel.status == TaskContentStatusEnum.closed) \
            .all()
    else:
        tasks = session.query(TaskContentModel) \
            .filter(TaskContentModel.content_linkbuilder_id == current_user.id) \
            .filter(TaskContentModel.status == TaskContentStatusEnum.closed) \
            .all()
    return tasks


@router.get(
    "/my/in-edit",
    response_model=list[TaskContentReadSerializer],
    status_code=fa.status.HTTP_200_OK,
)
async def tasks_content_list_my_closed(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        session: Session = fa.Depends(get_session_dependency),
):
    """
    get in edit content tasks for current user with content_teamlead or content_author roles"""
    if current_user.is_content_teamlead:
        tasks = session.query(TaskContentModel) \
            .filter(TaskContentModel.content_teamlead_id == current_user.id) \
            .filter(TaskContentModel.status == TaskContentStatusEnum.in_edit) \
            .all()
    elif current_user.is_content_author:
        tasks = session.query(TaskContentModel) \
            .filter(TaskContentModel.content_author_id == current_user.id) \
            .filter(TaskContentModel.status == TaskContentStatusEnum.in_edit) \
            .all()
    else:
        raise fa.HTTPException(status_code=404,
                               detail="'in edit' status is for content_teamlead or content_author only")
    return tasks


@router.get(
    "/{task_id}",
    response_model=TaskContentReadSerializer,
    status_code=fa.status.HTTP_200_OK,
)
@auth_head_only
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


@router.put(
    "/{task_id}",
    response_model=TaskContentReadSerializer,
    status_code=fa.status.HTTP_202_ACCEPTED,
)
async def task_content_update(
        task_id: int,
        task_content_ser: TaskContentUpdateSerializer,
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
):
    """
    update task by id
    """
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
    creates task by linkbuilder, sets task.content_teamlead_viewed=False
    """
    task_content_ser.content_linkbuilder_id = current_user.id
    task_content_ser.content_teamlead_viewed = False
    task_content = repo.create(TaskContentModel, task_content_ser)
    return task_content


@router.post(
    "/close/{task_id}",
    response_model=TaskContentReadSerializer,
)
async def task_content_close(
        task_id: int,
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
):
    """
    close task by id
    """
    task_content = repo.get(TaskContentModel, id=task_id)
    task_content = repo.update(task_content, {'status': TaskContentStatusEnum.closed,
                                              'closed_at': datetime.now()})
    return task_content


@router.delete(
    "/{task_id}",
)
async def task_content_delete(
        task_id: int,
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
):
    task_content = repo.get(TaskContentModel, id=task_id)
    if task_content is None:
        raise fa.HTTPException(status_code=404, detail="task not found")

    repo.remove(TaskContentModel, id=task_id)
    return {'message': 'ok'}
