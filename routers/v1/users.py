import fastapi as fa
from sqlalchemy import desc, asc, or_
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from services.notificator.celery_tasks import notify_users_all
from core.dependencies import (
    get_current_user_dependency,
    get_session_dependency,
    pagination_params_dependency
)
from core.enums import UserOrderByEnum, OrderEnum
from core.exceptions import UnauthorizedException
from database.crud import create, get, update, get_query_all_active
from database.models.link_url_domain import LinkUrlDomainModel
from database.models.user import UserModel
from database.repository import SqlAlchemyRepository
from database.schemas.user import (
    UserUpdateSerializer,
    UserCreateSerializer,
    UserReadSerializer,
    UserReadTeamleadSerializer, UserReadContentTeamleadSerializer,
)
from services.keycloak.keycloak import KCAdmin
from services.keycloak.celery_tasks import fetch_user_from_keycloak

router = fa.APIRouter()


@router.get("/", response_model=list[UserReadTeamleadSerializer])
def users_list(
        session: Session = fa.Depends(get_session_dependency),
        order_by: UserOrderByEnum = UserOrderByEnum.id,
        order: OrderEnum = OrderEnum.asc,
        pagination_params: dict = fa.Depends(pagination_params_dependency),
):
    """list all active users with optionals query params for being:
    -ordered (default is ascending by id)
    paginated (default all none)"""
    users = SqlAlchemyRepository(session).get_all_active_ordered_limited_offset(
        UserModel,
        order,
        order_by,
        pagination_params.get('limit'),
        pagination_params.get('offset'),
    )
    return users


@router.get("/inactive", response_model=list[UserReadTeamleadSerializer])
def users_inactive_list(
        session: Session = fa.Depends(get_session_dependency),
        order_by: UserOrderByEnum = UserOrderByEnum.id,
        order: OrderEnum = OrderEnum.asc,
        pagination_params: dict = fa.Depends(pagination_params_dependency),
):
    """list all inactive users ordered and paginated"""
    users = SqlAlchemyRepository(session).get_all_inactive_ordered_limited_offset(
        UserModel,
        order,
        order_by,
        pagination_params.get('limit'),
        pagination_params.get('offset'),
    )
    return users


@router.get("/my-linkbuilders", response_model=list[UserReadTeamleadSerializer])
def users_list_my_linkbuilders(
        session: Session = fa.Depends(get_session_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    users = SqlAlchemyRepository(session).get_query_all_active(UserModel, teamlead_id=current_user.id).all()
    return users


@router.get("/me", response_model=UserReadTeamleadSerializer)
def users_read_me(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    return current_user


@router.get("/me-and-my-linkbuilders", response_model=list[UserReadTeamleadSerializer])
def users_list_me_and_my_linkbuilders(
        session: Session = fa.Depends(get_session_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    users = SqlAlchemyRepository(session).get_query_all_active(UserModel, teamlead_id=current_user.id).all()
    users.append(current_user)
    users = list(set(users))
    return users


@router.get("/teamleads", response_model=list[UserReadSerializer])
def users_list_teamleads(
        session: Session = fa.Depends(get_session_dependency)
):
    users = SqlAlchemyRepository(session) \
        .get_query_all_active(UserModel) \
        .filter(UserModel.is_teamlead == True) \
        .all()
    return users


@router.get("/{user_id}", response_model=UserReadTeamleadSerializer)
def users_read(
        user_id: int,
        session: Session = fa.Depends(get_session_dependency)
):
    user = SqlAlchemyRepository(session).get(UserModel, id=user_id)
    if user is None:
        raise fa.HTTPException(status_code=404, detail="user not found")
    return user


@router.get("/linkers/all", response_model=list[UserReadTeamleadSerializer])
def users_list_linkers(
        session: Session = fa.Depends(get_session_dependency),
        order_by: UserOrderByEnum = UserOrderByEnum.id,
        order: OrderEnum = OrderEnum.asc,
        offset: int | None = None, limit: int | None = None,
):
    active_users_query = get_query_all_active(session, UserModel) \
        .filter(or_(
        UserModel.is_seo == False,
        UserModel.is_content_author == False,
        UserModel.is_content_teamlead == False,
    ))
    if order == OrderEnum.desc:
        users = active_users_query.order_by(
            desc(text(order_by.value))).offset(offset).limit(limit).all()
    else:
        users = active_users_query.order_by(
            asc(text(order_by.value))).offset(offset).limit(limit).all()

    return users


@router.get("/seo/all", response_model=list[UserReadTeamleadSerializer])
def users_list_seo(
        session: Session = fa.Depends(get_session_dependency),
        order_by: UserOrderByEnum = UserOrderByEnum.id,
        order: OrderEnum = OrderEnum.asc,
        offset: int | None = None, limit: int | None = None,
):
    active_users_query = get_query_all_active(session, UserModel) \
        .filter(UserModel.is_seo == True)
    if order == OrderEnum.desc:
        users = active_users_query.order_by(
            desc(text(order_by.value))).offset(offset).limit(limit).all()
    else:
        users = active_users_query.order_by(
            asc(text(order_by.value))).offset(offset).limit(limit).all()

    return users


@router.get("/content/all", response_model=list[UserReadContentTeamleadSerializer])
def users_list_linkers(
        session: Session = fa.Depends(get_session_dependency),
        order_by: UserOrderByEnum = UserOrderByEnum.id,
        order: OrderEnum = OrderEnum.asc,
        offset: int | None = None, limit: int | None = None,
):
    active_users_query = get_query_all_active(session, UserModel) \
        .filter(or_(
        UserModel.is_content_author == True,
        UserModel.is_content_teamlead == True,
    ))
    if order == OrderEnum.desc:
        users = active_users_query.order_by(
            desc(text(order_by.value))).offset(offset).limit(limit).all()
    else:
        users = active_users_query.order_by(
            asc(text(order_by.value))).offset(offset).limit(limit).all()

    return users


@router.get("/content/teamleads", response_model=list[UserReadSerializer])
def users_list_content_teamleads(
        session: Session = fa.Depends(get_session_dependency)
):
    users = SqlAlchemyRepository(session) \
        .get_query_all_active(UserModel) \
        .filter(UserModel.is_content_teamlead == True) \
        .all()
    return users


@router.get("/content/authors", response_model=list[UserReadContentTeamleadSerializer])
def users_list_content_authors(
        session: Session = fa.Depends(get_session_dependency),
        order_by: UserOrderByEnum = UserOrderByEnum.id,
        order: OrderEnum = OrderEnum.asc,
        offset: int | None = None, limit: int | None = None,
):
    active_users_query = get_query_all_active(session, UserModel) \
        .filter(UserModel.is_content_author == True)
    if order == OrderEnum.desc:
        users = active_users_query.order_by(
            desc(text(order_by.value))).offset(offset).limit(limit).all()
    else:
        users = active_users_query.order_by(
            asc(text(order_by.value))).offset(offset).limit(limit).all()

    return users


@router.post("/notify/all", status_code=fa.status.HTTP_201_CREATED)
def users_notify_all():
    task = notify_users_all.delay()
    return {'task_id': f'{task.task_id}'}


@router.post("/fetch-from-keycloack/me", status_code=fa.status.HTTP_201_CREATED)
def users_fetch_from_keycloack_me():
    """fetches from keycloack user mentioned in .envs/ as SUPERUSER and creates it at local database"""
    fetch_user_from_keycloak()
    return {'message': 'ok'}


@router.get("/fetch-from-keycloack/my-roles")
def users_keycloak_roles_my(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    """fetches from keycloack realm-level role-mappings of current user and returns them as list"""
    kc_admin = KCAdmin()
    roles = kc_admin.get_roles(current_user)
    return roles


@router.post("/", response_model=UserReadSerializer)
def users_create(
        user_ser: UserCreateSerializer,
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        seo_link_url_domains_id: list[int] = fa.Body(default=[]),
        session: Session = fa.Depends(get_session_dependency)
):
    if not current_user.is_head:
        raise UnauthorizedException

    user_ser.email = user_ser.email.lower()
    user_with_the_same_email = get(session, UserModel, email=user_ser.email)
    if user_with_the_same_email is not None:
        raise fa.HTTPException(status_code=400, detail="Email already registered")

    kc_admin = KCAdmin()
    kc_admin.create_user(user_ser)
    kc_user_uuid = kc_admin.get_user_uuid_by_email(user_ser.email)
    user_ser.uuid = kc_user_uuid

    user: UserModel = create(session, UserModel, user_ser)
    if user.is_head:
        kc_admin.set_role_head(user)
    if user.is_teamlead:
        kc_admin.set_role_teamlead(user)
    if user.is_seo:
        kc_admin.set_role_seo(user)
    if user.is_content_teamlead:
        kc_admin.set_role_content_teamlead(user)
    if user.is_content_author:
        kc_admin.set_role_content_author(user)
    if not user.is_head and not user.is_teamlead and not user.is_seo:
        kc_admin.set_role_linkbuilder(user)

    if seo_link_url_domains_id:
        seo_link_url_domains = session.query(LinkUrlDomainModel) \
            .where(LinkUrlDomainModel.id.in_(seo_link_url_domains_id)).all()
        user.seo_link_url_domains = seo_link_url_domains
        session.commit()
    kc_admin.send_request_verify_email_and_reset_password(user)
    return user


@router.put("/{user_id}", response_model=UserReadTeamleadSerializer)
async def users_update(
        user_id: int,
        user_ser: UserUpdateSerializer,
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        seo_link_url_domains_id: list[int] = fa.Body(default=[]),
        session: Session = fa.Depends(get_session_dependency),
):
    if not current_user.is_head:
        raise UnauthorizedException

    user: UserModel = get(session, UserModel, id=user_id)
    if user is None:
        raise fa.HTTPException(status_code=404, detail="user not found")

    if user_ser.email is not None and user_ser.email != user.email:
        user_ser.email = user_ser.email.lower()
        user_with_the_same_email = get(session, UserModel, email=user_ser.email)
        if user_with_the_same_email is not None:
            raise fa.HTTPException(status_code=400, detail="Email already registered")

    kc_admin = KCAdmin()
    kc_admin.update_user_credentials(user, user_ser)
    kc_admin.update_user_roles(user, user_ser)

    user = update(session, user, user_ser)

    seo_link_url_domains = session.query(LinkUrlDomainModel) \
        .where(LinkUrlDomainModel.id.in_(seo_link_url_domains_id)).all()
    user.seo_link_url_domains = seo_link_url_domains
    session.commit()
    return user


@router.put("/send-request-verify-email-and-reset-password/{user_id}", response_model=UserReadTeamleadSerializer)
async def users_update(
        user_id: int,
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        session: Session = fa.Depends(get_session_dependency)
):
    if not current_user.is_head:
        raise UnauthorizedException

    user = SqlAlchemyRepository(session).get(UserModel, id=user_id)
    if user is None:
        raise fa.HTTPException(status_code=404, detail="user not found")

    kc_admin = KCAdmin()
    kc_admin.send_request_verify_email_and_reset_password(user)
    return user


@router.delete("/{user_id}")
async def users_deactivate(
        user_id: int,
        session: Session = fa.Depends(get_session_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    if not current_user.is_head:
        raise UnauthorizedException

    user = SqlAlchemyRepository(session).get(UserModel, id=user_id)
    if user is None:
        raise fa.HTTPException(status_code=404, detail="user not found")

    kc_admin = KCAdmin()
    kc_admin.deactivate_user(user)
    user.is_active = False
    session.commit()

    return {'message': 'ok'}


@router.post("/activate/{user_id}")
async def users_activate(
        user_id: int,
        session: Session = fa.Depends(get_session_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    if not current_user.is_head:
        raise UnauthorizedException

    user = SqlAlchemyRepository(session).get(UserModel, id=user_id)
    if user is None:
        raise fa.HTTPException(status_code=404, detail="user not found")
    if user.is_active:
        raise fa.HTTPException(status_code=fa.status.HTTP_400_BAD_REQUEST,
                               detail='This user is active already')

    kc_admin = KCAdmin()
    kc_admin.activate_user(user)
    user.is_active = True
    session.commit()
    return {'message': 'ok'}


@router.delete("/remove/{user_id}")
async def users_remove(
        user_id: int,
        session: Session = fa.Depends(get_session_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    if not current_user.is_head:
        raise UnauthorizedException

    repo = SqlAlchemyRepository(session)
    user = repo.get(UserModel, id=user_id)
    if user is None:
        raise fa.HTTPException(status_code=404, detail="user not found")

    kc_admin = KCAdmin()
    kc_admin.remove_user(user)
    repo.remove(UserModel, user_id)
    return {'message': 'ok'}


@router.put("/me/set-telegram-id", response_model=UserReadTeamleadSerializer)
def users_me_set_telegram_id(
        user_ser: UserUpdateSerializer,
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        session: Session = fa.Depends(get_session_dependency),
):
    """
    set telegram id to current user
    """
    current_user.telegram_id = user_ser.telegram_id
    session.commit()
    session.refresh(current_user)
    return current_user


@router.put("/me/enable-disable-notification-telegram", response_model=UserReadTeamleadSerializer)
def users_me_enable_disable_notification_telegram(
        user_ser: UserUpdateSerializer,
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        session: Session = fa.Depends(get_session_dependency),
):
    """
    update current_user.is_accepting_telegram
    """
    if not current_user.telegram_id:
        raise fa.HTTPException(status_code=fa.status.HTTP_400_BAD_REQUEST,
                               detail='You should login with Telegram firstly to set telegram_id!')
    current_user.is_accepting_telegram = user_ser.is_accepting_telegram
    session.commit()
    session.refresh(current_user)
    return current_user


@router.put("/me/enable-disable-notification-email", response_model=UserReadTeamleadSerializer)
def users_me_enable_disable_notification_email(
        user_ser: UserUpdateSerializer,
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        session: Session = fa.Depends(get_session_dependency),
):
    """
    update current_user.is_accepting_emails
    """
    current_user.is_accepting_emails = user_ser.is_accepting_emails
    session.commit()
    session.refresh(current_user)
    return current_user
