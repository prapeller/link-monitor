import datetime

import fastapi as fa
from fastapi_resource_server import JwtDecodeOptions, OidcResourceServer
from sqlalchemy.orm import Session

from core.config import settings
from core.enums import LinkStatusEnum
from database import Base, SessionLocal, SessionInMemory, in_memory_engine
from database.models.user import UserModel
from database.repository import SqlAlchemyRepository


def get_session_dependency():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_sqlalchemy_repo_dependency():
    session = SessionLocal()

    repo = SqlAlchemyRepository(session)
    try:
        yield repo
    finally:
        session.close()


decode_options = JwtDecodeOptions(verify_aud=False)

oauth2_scheme = OidcResourceServer(
    issuer=f"{settings.KEYCLOAK_BASE_URL}/realms/{settings.KEYCLOAK_REALM_APP}",
    jwt_decode_options=decode_options,
)


async def get_current_user_dependency(session: Session = fa.Depends(get_session_dependency),
                                      keycloak_data: dict = fa.Security(oauth2_scheme)) -> UserModel | None:
    try:
        current_user = SqlAlchemyRepository(session).get(UserModel, email=keycloak_data.get('email'))
        return current_user
    except fa.HTTPException:
        return None


async def get_current_user_roles_dependency(keycloak_data: dict = fa.Security(oauth2_scheme)) -> list:
    current_user_roles: list = keycloak_data.get('realm_access').get('roles')
    return current_user_roles


async def link_params_dependency(
        # query_params '&link_url_domain_name=20bet.tv&link_url_domain_name=20-bet.in'
        # will be interpreted to filter_params['link_url_domain_name'] = ['20bet.tv', '20-bet.in']
        user_id: int | None = None,
        link_url_domain_name: list[str] | None = fa.Query(None),
        page_url: str | None = None,
        link_url: str | None = None,
        anchor: str | None = None,
        da: float | None = None,
        dr: float | None = None,
        price: float | None = None,
        screenshot_url: str | None = None,
        contact: str | None = None,
        link_check_last_status: LinkStatusEnum = None,
        link_check_last_result_message: str | None = None,
        link_check_last_created_at: str | None = None,
):
    return {
        'user_id': user_id,
        'link_url_domain_name': link_url_domain_name,
        'page_url': page_url,
        'link_url': link_url,
        'anchor': anchor,
        'da': da,
        'dr': dr,
        'price': price,
        'screenshot_url': screenshot_url,
        'contact': contact,
        'link_check_last_status': link_check_last_status,
        'link_check_last_result_message': link_check_last_result_message,
        'link_check_last_created_at': link_check_last_created_at,
    }


def pudomain_params_dependency(
        name: str | None = None,
        link_da_last_from: float | None = None,
        link_da_last_upto: float | None = None,
        link_dr_last_from: float | None = None,
        link_dr_last_upto: float | None = None,
        link_price_avg_from: float | None = None,
        link_price_avg_upto: float | None = None,
        language_tags_id: list[str] | None = fa.Query(None),
        country_tags_id: list[str] | None = fa.Query(None),
):
    return {
        'name': name,
        'link_da_last_from': link_da_last_from,
        'link_da_last_upto': link_da_last_upto,
        'link_dr_last_from': link_dr_last_from,
        'link_dr_last_upto': link_dr_last_upto,
        'link_price_avg_from': link_price_avg_from,
        'link_price_avg_upto': link_price_avg_upto,
        'language_tags_id': language_tags_id,
        'country_tags_id': country_tags_id,
    }


async def pagination_params_dependency(
        offset: int | None = None,
        limit: int | None = None,
):
    return {
        'offset': offset,
        'limit': limit,
    }


async def period_params_dependency(
        date_from: datetime.date | None = datetime.date.today(),
        date_upto: datetime.date | None = datetime.date.today(),
):
    return {
        'date_from': date_from,
        'date_upto': date_upto,
    }
