import datetime

import fastapi as fa
import sqlalchemy as sa
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from core.dependencies import (get_db_dependency, get_current_user_dependency, period_params_dependency,
                               link_params_dependency_v2)
from core.enums import LinkOrderByEnum, OrderEnum
from database.crud import get_query_all_active, get
from database.models.link import LinkModel
from database.models.link_url_domain import LinkUrlDomainModel
from database.models.user import UserModel
from database.schemas.user import DashboardUserDataResponseModel
from core.shared import filter_query_by_period_params, filter_query_by_link_params
from services.file_handler import iterfile
from services.reporter.based_link.generator import generate_filtered_links_report
from services.reporter.based_link.generator import get_dashboard_data
from services.reporter.based_link_url_domain.generator import (
    generate_report_v2 as generate_link_url_domain_report,
    generate_report_ui_v2 as generate_link_url_domain_report_ui
)

router = fa.APIRouter()


@router.get("/dashboard/head",
            response_model=list[DashboardUserDataResponseModel])
async def get_report_dashboard_head(
        db: Session = fa.Depends(get_db_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        period_params=fa.Depends(period_params_dependency)
):
    """returns dashboard table data on
    'Dashboard' button for Head"""
    if not current_user.is_head:
        raise fa.HTTPException(status_code=fa.status.HTTP_401_UNAUTHORIZED,
                               detail='Only head user can view dashboard for all users')
    users = get_query_all_active(db, UserModel).all()

    date_from = period_params['date_from']
    date_upto = period_params['date_upto']
    dashboard_data = get_dashboard_data(db=db, users=users, date_from=date_from, date_upto=date_upto)

    return dashboard_data


@router.get("/dashboard/teamlead",
            response_model=list[DashboardUserDataResponseModel])
async def get_report_dashboard_teamlead(
        db: Session = fa.Depends(get_db_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        period_params=fa.Depends(period_params_dependency)
):
    """returns dashboard table data on
    'Dashboard' button for Teamlead"""
    if not current_user.is_teamlead:
        raise fa.HTTPException(status_code=fa.status.HTTP_401_UNAUTHORIZED,
                               detail='Only teamlead user can view dashboard for his linkbuilders')
    users = get_query_all_active(db, UserModel).filter_by(teamlead_id=current_user.id).all()
    users.append(current_user)
    users = list(set(users))

    date_from = period_params['date_from']
    date_upto = period_params['date_upto']
    dashboard_data = get_dashboard_data(db=db, users=users, date_from=date_from, date_upto=date_upto)

    return dashboard_data


@router.get("/link_url_domains/{id}/users/all/ui")
async def get_report_link_url_domains_id_users_all_ui(
        id: int,
        db: Session = fa.Depends(get_db_dependency),
        year: int | None = datetime.datetime.now().year,
):
    """returns report table data on
    'Project.id' button for Head/Teamlead"""
    link_url_domain = get(db, LinkUrlDomainModel, id=id)
    if link_url_domain is None:
        raise fa.HTTPException(status_code=404, detail="Project (link_url_domain) not found")
    link_url_domains = [link_url_domain]
    users = db.query(UserModel).all()
    return generate_link_url_domain_report_ui(db=db,
                                              link_url_domains=link_url_domains,
                                              users=users,
                                              year=year)


@router.get("/link_url_domains/{id}/users/all")
async def get_report_link_url_domains_id_users_all(
        id: int,
        db: Session = fa.Depends(get_db_dependency),
        year: int | None = datetime.datetime.now().year,
):
    """returns report file.xlsx on
    'Project.id' button for Head/Teamlead"""
    to_save_filepath = 'static/report/report.xlsx'
    link_url_domain = get(db, LinkUrlDomainModel, id=id)
    if link_url_domain is None:
        raise fa.HTTPException(status_code=404, detail="Project (link_url_domain) not found")
    link_url_domains = [link_url_domain]
    users = db.query(UserModel).all()
    generate_link_url_domain_report(db=db,
                                    template_filename='static/report/report_template.xlsx',
                                    to_save_filepath=to_save_filepath,
                                    link_url_domains=link_url_domains,
                                    users=users,
                                    year=year)

    return StreamingResponse(iterfile(filepath=to_save_filepath))


@router.get("/links/filtered")
async def get_report_links_filtered(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        db: Session = fa.Depends(get_db_dependency),
        links_order_by: LinkOrderByEnum = LinkOrderByEnum.created_at,
        links_order: OrderEnum = OrderEnum.desc,
        period_params: dict = fa.Depends(period_params_dependency),
        links_params: dict = fa.Depends(link_params_dependency_v2),
):
    """returns filtered links file.xlsx on
    'Get Filtered Links' button for Head/Teamlead/Linkbuilder/Seo
    Frontend sends links_order_by, links_order, period_params and links_params
    as lastly user have selected at 'Links' page or default if he hasn't selected anything yet"""

    to_save_filepath = f'static/links/links_filtered_for_user_uuid_{current_user.uuid}.xlsx'

    if current_user.is_head:
        links_query = db.query(LinkModel)
    elif current_user.is_teamlead:
        users_id_to_view_list = [linkbuilder.id for linkbuilder in current_user.linkbuilders] + [
            current_user.id]
        links_query = db.query(LinkModel).filter(LinkModel.user_id.in_(users_id_to_view_list))
    else:
        links_query = db.query(LinkModel).filter(LinkModel.user_id == current_user.id)
    links_query = filter_query_by_period_params(links_query, period_params)
    links_query = filter_query_by_link_params(links_query, links_params, LinkModel)
    order = sa.desc if links_order.value == 'desc' else sa.asc
    links_query = links_query.order_by(order(getattr(LinkModel, links_order_by)))
    links = links_query.all()
    generate_filtered_links_report(links=links,
                                   template_filename='static/links/links_filtered_download_template.xlsx',
                                   to_save_filepath=to_save_filepath)

    return StreamingResponse(iterfile(filepath=to_save_filepath))
