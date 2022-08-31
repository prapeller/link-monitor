import re

import fastapi as fa
import sqlalchemy as sa
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from core.dependencies import get_db_dependency, get_current_user_dependency
from database.crud import get, remove
from database.models.link import LinkModel
from database.models.link_url_domain import LinkUrlDomainModel
from database.models.page_url_domain import PageUrlDomainModel
from database.models.user import UserModel
from database.schemas.page_url_domain import PageUrlDomainReadSerializer, BaseCheckResponseModel
from core.shared import get_domain_name_from_url

router = fa.APIRouter()


@router.get("/", response_model=list[PageUrlDomainReadSerializer])
def page_url_domains_list(
        db: Session = fa.Depends(get_db_dependency),
):
    link_url_domains = db.query(PageUrlDomainModel).all()
    return link_url_domains


@router.post("/base-check", response_model=BaseCheckResponseModel)
def page_url_domains_base_check(
        db: Session = fa.Depends(get_db_dependency),
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

    page_url_domains_tuples: list[tuple] = db.execute(
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


@router.delete("/{page_url_domain_id}")
async def page_url_domains_delete(
        page_url_domain_id: int,
        db: Session = fa.Depends(get_db_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    if not current_user.is_head:
        raise fa.HTTPException(status_code=fa.status.HTTP_401_UNAUTHORIZED,
                               detail='Only head user can delete link_url_domain')
    page_url_domain = get(db, PageUrlDomainModel, id=page_url_domain_id)
    if page_url_domain is None:
        raise fa.HTTPException(status_code=404, detail="link_url_domain not found")

    remove(db, PageUrlDomainModel, page_url_domain_id)
    return {'message': 'ok'}
