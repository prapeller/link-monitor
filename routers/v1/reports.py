import fastapi as fa
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from core.dependencies import get_session_dependency, get_current_user_dependency
from database.models.link_url_domain import LinkUrlDomainModel
from database.models.user import UserModel
from services.file_handler.file_handler import iterfile
from services.reporter.based_link.generator import generate_report as generate_links_report
from services.reporter.based_link_url_domain.generator import (
    generate_report as generate_link_url_domain_report
)

router = fa.APIRouter()


@router.get("/link_url_domains/all/users/all")
def get_report_link_url_domains_all_users_all(
        db: Session = fa.Depends(get_session_dependency)
):
    """returns report file.xlsx on
    'Get Report' button for Head"""
    to_save_filepath = 'static/report/report.xlsx'
    link_url_domains = db.query(LinkUrlDomainModel).all()
    users = db.query(UserModel).all()
    generate_link_url_domain_report(db=db,
                                    template_filename='static/report/report_template.xlsx',
                                    to_save_filepath=to_save_filepath,
                                    link_url_domains=link_url_domains,
                                    users=users)

    return StreamingResponse(iterfile(filepath=to_save_filepath))


@router.get("/link_url_domains/all/users/my-linkbuilders")
def get_report_link_url_domains_all_users_my_linkbuilders(
        db: Session = fa.Depends(get_session_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency)
):
    """returns report file.xlsx on
    'Get Report' button for Teamlead"""
    to_save_filepath = 'static/report/report.xlsx'
    link_url_domains = db.query(LinkUrlDomainModel).all()
    users = [user for user in current_user.linkbuilders]
    generate_link_url_domain_report(db=db,
                                    template_filename='static/report/report_template.xlsx',
                                    to_save_filepath=to_save_filepath,
                                    link_url_domains=link_url_domains,
                                    users=users)

    return StreamingResponse(iterfile(filepath=to_save_filepath))


@router.get("/link_url_domains/all/users/me")
def get_report_link_url_domains_all_users_me(
        db: Session = fa.Depends(get_session_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency)
):
    """returns report file.xlsx on
    'Get Report' button for Linkbuilder"""
    to_save_filepath = 'static/report/report.xlsx'
    link_url_domains = db.query(LinkUrlDomainModel).all()
    users = [current_user]
    generate_link_url_domain_report(db=db,
                                    template_filename='static/report/report_template.xlsx',
                                    to_save_filepath=to_save_filepath,
                                    link_url_domains=link_url_domains,
                                    users=users)

    return StreamingResponse(iterfile(filepath=to_save_filepath))


@router.get("/links/all/users/me")
def get_report_links_all_users_me(
        db: Session = fa.Depends(get_session_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency)
):
    """returns links file.xlsx on
    'Get My Links' button for Head/Teamlead/Linkbuilder"""
    to_save_filepath = f'static/links/links_for_user_uuid_{current_user.uuid}.xlsx'
    generate_links_report(user=current_user,
                          db=db,
                          template_filename='static/links/links_download_template.xlsx',
                          to_save_filepath=to_save_filepath)

    return StreamingResponse(iterfile(filepath=to_save_filepath))
