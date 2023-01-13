import re

import fastapi as fa
import sqlalchemy as sa
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from core.dependencies import (
    get_session_dependency,
    period_params_dependency,
    get_current_user_dependency,
    pudomain_params_dependency,
    pagination_params_dependency
)
from core.enums import PUDomainOrderByEnum, OrderEnum
from core.exceptions import UnauthorizedException
from core.shared import (
    filter_query_by_period_params_pudomain_link,
    filter_query_by_model_params_pudomain,
    paginate_query
)
from database.crud import get, remove
from database.models.link import LinkModel
from database.models.link_url_domain import LinkUrlDomainModel
from database.models.page_url_domain import PageUrlDomainModel
from database.models.tag import TagModel
from database.models.user import UserModel
from database.repository import SqlAlchemyRepository
from database.schemas.page_url_domain import (
    PageUrlDomainReadSerializer,
    BaseCheckResponseModel,
    PUDomainReadLastLinkManyTotalCountResponseModel,
    PUDomainReadLastLinkSerializer, PageUrlDomainUpdateSerializer
)
from services.domain_checker.domain_checker import (
    PageUrlDomainChecker,
    get_domain_name_from_url
)
from services.domain_checker.celery_tasks import check_pudomains_with_similarweb

router = fa.APIRouter()


@router.get("/",
            response_model=list[PageUrlDomainReadSerializer]
            )
def page_url_domains_list(
        session: Session = fa.Depends(get_session_dependency),
):
    repo = SqlAlchemyRepository(session)
    page_url_domains = repo.get_all(PageUrlDomainModel)
    return page_url_domains


@router.get("/donor-domains",
            response_model=PUDomainReadLastLinkManyTotalCountResponseModel
            )
def page_url_domains_list(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        session: Session = fa.Depends(get_session_dependency),
        pudomain_order_by: PUDomainOrderByEnum = PUDomainOrderByEnum.link_created_at_last,
        pudomain_order: OrderEnum = OrderEnum.desc,
        period_params: dict = fa.Depends(period_params_dependency),
        pudomain_params: dict = fa.Depends(pudomain_params_dependency),
        pagination_params: dict = fa.Depends(pagination_params_dependency),
):
    if not current_user.is_head:
        raise UnauthorizedException

    pudomains_query = session.query(PageUrlDomainModel)
    total_domains_count = pudomains_query.count()
    pudomains_query = filter_query_by_period_params_pudomain_link(pudomains_query, period_params)
    pudomains_query = filter_query_by_model_params_pudomain(pudomains_query, pudomain_params)
    filtered_domains_count = pudomains_query.count()
    pudomains_query = paginate_query(PageUrlDomainModel, pudomains_query, pudomain_order_by, pudomain_order,
                                     pagination_params)
    pudomains = pudomains_query.all()
    pud_ser_out_list = [PUDomainReadLastLinkSerializer.from_orm(pud) for pud in pudomains]
    pud_ser_out_list_json = jsonable_encoder(pud_ser_out_list)

    return JSONResponse({'domains_read_last_links': pud_ser_out_list_json,
                         'total_domains_count': total_domains_count,
                         'filtered_domains_count': filtered_domains_count})


@router.get("/{pud_id}",
            response_model=PUDomainReadLastLinkSerializer
            )
def page_url_domains_read(
        pud_id: int = fa.Path(...),
        session: Session = fa.Depends(get_session_dependency),
):
    repo = SqlAlchemyRepository(session)
    page_url_domain = repo.get(PageUrlDomainModel, id=pud_id)
    if page_url_domain is None:
        raise fa.HTTPException(status_code=404, detail="PageUrlDomain not found")
    return page_url_domain


@router.post("/base-check",
             response_model=BaseCheckResponseModel
             )
def page_url_domains_base_check(
        session: Session = fa.Depends(get_session_dependency),
        is_base: bool = True,
        check_str=fa.Body(...),
):
    """base check with possibility to choose which page_url_domains to compare to
    if is_base = True - then we compare only with those page_url_domains that are
    from 'base' projects (ie link.link_url_domain.is_base = True)
    if is_base = False - then we compare with any page_url_domains that our links have
    """
    check_links: list[str] = re.split(r"[,\n ]", check_str)
    check_domains = [get_domain_name_from_url(link) for link in check_links if link]

    page_url_domains_tuples: list[tuple] = session.execute(
        sa.select(PageUrlDomainModel.name, LinkUrlDomainModel.name, LinkUrlDomainModel.is_base)
        .select_from(
            sa.join(LinkModel, LinkUrlDomainModel).join(PageUrlDomainModel)
        )
        .filter(sa.text('link_url_domain.is_base is true') if is_base else sa.text(''))
    ).all()
    page_url_domains = [domain_tuple[0] for domain_tuple in page_url_domains_tuples]
    present = []
    not_present = []
    for domain in check_domains:
        if domain in page_url_domains:
            present.append(domain)
        else:
            not_present.append(domain)
    present = list(set(present))
    not_present = list(set(not_present))

    return JSONResponse({'present': present, 'not_present': not_present})


@router.post(
    "/check-with-similarweb",
)
async def page_url_domains_check_with_similarweb(
        pudomain_id_list: list[int] = fa.Body(...),
        sync_mode: bool = fa.Query(default=False),
):
    if sync_mode:
        pudomain_checker = PageUrlDomainChecker(pudomain_id_list)
        await pudomain_checker.run_check()
        return {'message': 'ok'}
    else:
        task = check_pudomains_with_similarweb.delay(id_list=pudomain_id_list)
        return JSONResponse(content={"task_id": task.task_id})


@router.put("/{pud_id}",
            response_model=PUDomainReadLastLinkSerializer
            )
async def page_url_domains_update(
        pud_ser: PageUrlDomainUpdateSerializer,
        pud_id: int = fa.Path(...),
        session: Session = fa.Depends(get_session_dependency),
):
    """
    update page_url_domain by id
    """
    repo = SqlAlchemyRepository(session)
    page_url_domain = repo.get(PageUrlDomainModel, id=pud_id)
    if page_url_domain is None:
        raise fa.HTTPException(status_code=404, detail="PageUrlDomain not found")
    tags_id = pud_ser.tags_id
    tags = repo.get_many_by_id(TagModel, tags_id)
    repo.update(page_url_domain, pud_ser)
    page_url_domain.tags = tags
    session.commit()

    return page_url_domain


@router.delete("/{pud_id}")
async def page_url_domains_delete(
        pud_id: int,
        session: Session = fa.Depends(get_session_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    if not current_user.is_head:
        raise UnauthorizedException

    page_url_domain = get(session, PageUrlDomainModel, id=pud_id)
    if page_url_domain is None:
        raise fa.HTTPException(status_code=404, detail="link_url_domain not found")

    remove(session, PageUrlDomainModel, pud_id)
    return {'message': 'ok'}
