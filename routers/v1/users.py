import datetime as dt

import fastapi as fa
import pytz
import sqlalchemy as sa

from core.dependencies import (
    get_current_user_dependency,
    get_sqlalchemy_repo_dependency,
)
from core.shared import auth_head, auth_head_or_teamlead, auth_head_or_content_head
from core.timezones import TIMEZONES_DICT
from database.models.user import UserModel
from database.repository import SqlAlchemyRepository
from database.schemas.user import (
    UserUpdateSerializer,
    UserCreateSerializer,
    UserReadSerializer,
    UserReadTeamleadSerializer,
)
from services.keycloak.celery_tasks import fetch_user_from_keycloak
from services.keycloak.keycloak import KCAdmin
from services.notificator.celery_tasks import prepare_and_send_linkers_report_daily_messages

router = fa.APIRouter()


@router.get("/", response_model=list[UserReadTeamleadSerializer])
@auth_head
async def users_list(
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    """list all active users"""
    users = repo.get_query_all_active(UserModel).all()
    return users


@router.get("/inactive", response_model=list[UserReadTeamleadSerializer])
@auth_head
async def users_inactive_list(
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    """list all inactive users ordered and paginated"""
    users = repo.get_query_all_inactive(UserModel).all()
    return users


@router.get("/my-linkbuilders", response_model=list[UserReadTeamleadSerializer])
@auth_head_or_teamlead
async def users_list_my_linkbuilders(
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    users = repo.get_query_all_active(UserModel, teamlead_id=current_user.id).all()
    return users


@router.get("/me", response_model=UserReadTeamleadSerializer)
async def users_read_me(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    return current_user


@router.get("/me-and-my-linkbuilders", response_model=list[UserReadTeamleadSerializer])
@auth_head_or_teamlead
async def users_list_me_and_my_linkbuilders(
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    users = repo.get_query_all_active(UserModel, teamlead_id=current_user.id).all()
    users.append(current_user)
    users = list(set(users))
    return users


@router.get("/teamleads", response_model=list[UserReadSerializer])
@auth_head_or_teamlead
async def users_list_teamleads(
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    users = repo.get_query_all_active(UserModel, is_teamlead=True).all()
    return users


@router.get("/{user_id}", response_model=UserReadTeamleadSerializer)
@auth_head
async def users_read(
        user_id: int,
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    user = repo.get(UserModel, id=user_id)
    return user


@router.get("/linkers/all", response_model=list[UserReadTeamleadSerializer])
@auth_head
async def users_list_linkers(
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    users = repo.get_query_all_active(UserModel).filter(sa.and_(
        UserModel.is_seo == False,
        UserModel.is_content_author == False,
        UserModel.is_content_teamlead == False,
        UserModel.is_content_head == False,
    )).all()
    return users


@router.get("/seo/all", response_model=list[UserReadTeamleadSerializer])
@auth_head
async def users_list_seo(
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    users = repo.get_query_all_active(UserModel, is_seo=True).all()
    return users


@router.get("/content/all", response_model=list[UserReadTeamleadSerializer])
@auth_head_or_content_head
async def users_list_linkers(
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    users = repo.get_query_all_active(UserModel).filter(sa.or_(
        UserModel.is_content_head == True,
        UserModel.is_content_teamlead == True,
        UserModel.is_content_author == True,
    )).all()
    return users


@router.get("/content/teamleads", response_model=list[UserReadSerializer])
async def users_list_content_teamleads(
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    users = repo.get_query_all_active(UserModel, is_content_teamlead=True).all()
    return users


@router.get("/content/my-content-authors", response_model=list[UserReadTeamleadSerializer])
@auth_head_or_teamlead
async def users_list_content_my_content_authors(
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    users = repo.get_query_all_active(UserModel, content_teamlead_id=current_user.id,
                                      is_content_author=True).all()
    return users


@router.post("/fetch-from-keycloack/me", status_code=fa.status.HTTP_201_CREATED)
async def users_fetch_from_keycloack_me():
    """fetches from keycloack user mentioned in .envs/ as SUPERUSER and creates it at local database"""
    fetch_user_from_keycloak()
    return {'message': 'ok'}


@router.get("/fetch-from-keycloack/my-roles")
@auth_head
async def users_fetch_from_keycloak_my_roles(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    """fetches from keycloack realm-level role-mappings of current user and returns them as list"""
    roles = KCAdmin().get_user_roles(current_user)
    return roles


@router.post("/", response_model=UserReadSerializer)
@auth_head
async def users_create(
        user_ser: UserCreateSerializer,
        seo_link_url_domains_id: list[int] = fa.Body(default=[]),
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    user_ser.lower_email()
    repo.check_if_user_already_registered(user_ser)

    kc_admin = KCAdmin()
    kc_admin.create_user(user_ser)
    kc_user_uuid = kc_admin.get_user_uuid_by_email(user_ser.email)
    user_ser.uuid = kc_user_uuid

    user: UserModel = repo.create(UserModel, user_ser)
    kc_admin.set_user_roles(user)
    user = repo.update_users_seo_link_url_domains(user, seo_link_url_domains_id)
    kc_admin.send_request_verify_email_and_reset_password(user)
    return user


@router.put("/{user_id}", response_model=UserReadTeamleadSerializer)
async def users_update(
        user_id: int,
        user_ser: UserUpdateSerializer,
        seo_link_url_domains_id: list[int] = fa.Body(default=[]),
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    user: UserModel = repo.get(UserModel, id=user_id)
    user_ser.lower_email()
    if user_ser.email != user.email:
        repo.check_if_user_already_registered(user_ser)

    kc_admin = KCAdmin()
    kc_admin.update_user_credentials(user, user_ser)
    kc_admin.update_user_roles(user, user_ser)

    user = repo.update(user, user_ser)
    user = repo.update_users_seo_link_url_domains(user, seo_link_url_domains_id)
    return user


@router.put("/send-request-verify-email-and-reset-password/{user_id}",
            response_model=UserReadTeamleadSerializer)
@auth_head
async def users_update(
        user_id: int,
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    user = repo.get(UserModel, id=user_id)
    KCAdmin().send_request_verify_email_and_reset_password(user)
    return user


@router.delete("/{user_id}")
@auth_head
async def users_deactivate(
        user_id: int,
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    user = repo.get(UserModel, id=user_id)
    KCAdmin().deactivate_user(user)
    repo.deactivate_user(user)
    return {'message': 'ok'}


@router.post("/activate/{user_id}")
@auth_head
async def users_activate(
        user_id: int,
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    user = repo.get(UserModel, id=user_id)
    KCAdmin().activate_user(user)
    repo.activate_user(user)
    return {'message': 'ok'}


@router.delete("/remove/{user_id}")
@auth_head
async def users_remove(
        user_id: int,
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    user = repo.get(UserModel, id=user_id)
    KCAdmin().remove_user(user)
    repo.remove(UserModel, user_id)
    return {'message': 'ok'}


@router.get(
    "/timezones/all",
    status_code=fa.status.HTTP_200_OK,
)
async def users_get_timezones():
    """
    get timezones dict
    """
    return TIMEZONES_DICT


@router.get(
    "/timezones/my/current-time",
    status_code=fa.status.HTTP_200_OK,
)
async def users_get_timezones(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    """return current time of current user"""
    return dt.datetime.now(pytz.timezone(TIMEZONES_DICT[current_user.timezone]))


@router.post("/prepare-and-send-linkers-report-daily-messages", status_code=fa.status.HTTP_201_CREATED)
@auth_head
async def users_prepare_linkers_report_daily_messages(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        sync_mode: bool = fa.Query(default=False),
):
    """creates pending daily report messages for linkers """
    if sync_mode:
        prepare_and_send_linkers_report_daily_messages()
        return {'message': 'ok'}
    else:
        task = prepare_and_send_linkers_report_daily_messages.delay()
        return fa.responses.JSONResponse(content={"task_id": task.task_id})
