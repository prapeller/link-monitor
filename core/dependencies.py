import datetime

from fastapi import Security, Depends
from fastapi_resource_server import JwtDecodeOptions, OidcResourceServer
from sqlalchemy.orm import Session

from core.config import settings
from database import SessionLocal
from database.crud import get
from database.models.user import UserModel
from core.enums import LinkStatusEnum


def get_db_dependency():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


decode_options = JwtDecodeOptions(verify_aud=False)

oauth2_scheme = OidcResourceServer(
    issuer=f"{settings.KEYCLOAK_BASE_URL}/realms/{settings.KEYCLOAK_REALM_APP}",
    jwt_decode_options=decode_options,
)


async def get_current_user_dependency(db: Session = Depends(get_db_dependency),
                                      keycloak_data: dict = Security(oauth2_scheme)) -> UserModel:
    current_user = get(db, UserModel, email=keycloak_data.get('email'))
    return current_user


async def link_params_dependency_v1(
        user_id: int | None = None,
        link_url_domain_name: str | None = None,
        page_url: str | None = None,
        link_url: str | None = None,
        anchor: str | None = None,
        da: float | None = None,
        dr: float | None = None,
        price: float | None = None,
        screenshot_url: str | None = None,
        contact: str | None = None,
        created_at: str | None = None,
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
        'created_at': created_at,
        'link_check_last_status': link_check_last_status,
        'link_check_last_result_message': link_check_last_result_message,
        'link_check_last_created_at': link_check_last_created_at,
    }


async def link_params_dependency_v2(
        user_id: int | None = None,
        link_url_domain_name: str | None = None,
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


async def pagination_params_dependency(
        offset: int | None = None,
        limit: int | None = None,
        year: int | None = datetime.datetime.now().year,
):
    return {
        'offset': offset,
        'limit': limit,
        'year': year,
    }

async def pagination_params_dependency_v2(
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
