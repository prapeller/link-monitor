import fastapi as fa
import sqlalchemy as sa

from core.dependencies import (
    get_current_user_dependency,
    get_sqlalchemy_repo_dependency,
    year_month_period_params_dependency,
)
from core.shared import get_year_month_period
from database.models.content_data_dashboard import ContentDataModel
from database.models.user import UserModel
from database.repository import SqlAlchemyRepository
from database.schemas.content_data_dashboard import (
    ContentDataReadUsersSerializer,
    ContentDataUpdateSerializer,
)
from services.reporter.celery_tasks import check_if_content_data_created_on_tasks_all

router = fa.APIRouter()


@router.get("/content-head",
            response_model=list[ContentDataReadUsersSerializer])
async def content_data_list_for_content_head(
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
        year_month_period_params=fa.Depends(year_month_period_params_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    """
    for 'head/content_head' role
    returns content_data table data at 'Guest Posting' menu, 'Dashboard' tab
    """

    content_authors = repo.session.query(UserModel) \
        .where(sa.or_(UserModel.is_content_author == True, UserModel.is_content_teamlead == True)).all()
    year_month_period = get_year_month_period(year_month_period_params)
    content_data = repo.session.query(ContentDataModel) \
        .where(sa.and_(ContentDataModel.year_month.in_(year_month_period),
                       ContentDataModel.content_author_id.in_([user.id for user in content_authors]),
                       )).all()
    return content_data


@router.get("/content-teamlead",
            response_model=list[ContentDataReadUsersSerializer])
async def content_data_list_for_content_teamlead(
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
        year_month_period_params=fa.Depends(year_month_period_params_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    """
    for 'content_teamlead' role
    returns content_data table data at 'Guest Posting' menu, 'Dashboard as Teamlead' tab
    """
    content_authors = repo.session.query(UserModel).where(UserModel.content_teamlead_id == current_user.id).all()
    year_month_period = get_year_month_period(year_month_period_params)
    content_data = repo.session.query(ContentDataModel) \
        .where(sa.and_(ContentDataModel.year_month.in_(year_month_period),
                       ContentDataModel.content_author_id.in_([user.id for user in content_authors]),
                       )).all()
    return content_data


@router.get("/content-author",
            response_model=list[ContentDataReadUsersSerializer])
async def content_data_list_for_content_author(
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
        year_month_period_params=fa.Depends(year_month_period_params_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    """
    for 'content_author' role
    returns content_data table data at 'Guest Posting' menu, 'Dashboard' tab
    """
    year_month_period = get_year_month_period(year_month_period_params)
    content_data = repo.session.query(ContentDataModel) \
        .where(sa.and_(ContentDataModel.year_month.in_(year_month_period),
                       ContentDataModel.content_author_id == current_user.id,
                       )).all()
    return content_data


@router.post("/check_if_all_content_data_created_task")
async def content_data_check_if_all_content_data_created(
        sync_mode: bool = fa.Query(default=False),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    """
    check if all content_data created
    """
    if sync_mode:
        results = check_if_content_data_created_on_tasks_all()
        return {'message': results}
    else:
        task = check_if_content_data_created_on_tasks_all.delay()
        return fa.responses.JSONResponse(content={"task_id": task.task_id})


@router.put("/{id}",
            response_model=ContentDataReadUsersSerializer)
async def content_data_update(
        id: int,
        content_data_ser: ContentDataUpdateSerializer,
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    """
    for 'head' or 'content_head' role
    creates and returns content_data obj
    """
    content_data = repo.get(ContentDataModel, id=id)
    return repo.update(content_data, content_data_ser)
