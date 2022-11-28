import fastapi as fa
from sqlalchemy.orm import Session

from core.dependencies import get_session_dependency, get_current_user_dependency
from core.exceptions import UnauthorizedException
from database.crud import get, update
from database.models.link import LinkModel
from database.models.link_url_domain import LinkUrlDomainModel
from database.models.user import UserModel
from database.schemas.link_url_domain import LinkUrlDomainReadSerializerV2, LinkUrlDomainUpdateSerializerV2

router = fa.APIRouter()


@router.get("/my-seo", response_model=list[LinkUrlDomainReadSerializerV2])
def link_url_domains_list_my(
        db: Session = fa.Depends(get_session_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    link_url_domains = db.query(LinkUrlDomainModel) \
        .filter(LinkUrlDomainModel.id.in_(current_user.seo_link_url_domains_id)).all()
    return link_url_domains


@router.get("/my", response_model=list[LinkUrlDomainReadSerializerV2])
def link_url_domains_list_my(
        db: Session = fa.Depends(get_session_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    link_url_domains = db.query(LinkUrlDomainModel).join(LinkModel) \
        .filter(LinkModel.user_id == current_user.id).all()
    return link_url_domains


@router.get("/my-and-my-linkbuilders", response_model=list[LinkUrlDomainReadSerializerV2])
def link_url_domains_list_my_and_my_linkbuilders(
        db: Session = fa.Depends(get_session_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    if not current_user.is_teamlead:
        raise UnauthorizedException

    users_id_to_view_list = [linkbuilder.id for linkbuilder in current_user.linkbuilders] + [
        current_user.id]
    link_url_domains = db.query(LinkUrlDomainModel).join(LinkModel) \
        .filter(LinkModel.user_id.in_(users_id_to_view_list)).all()
    return link_url_domains


@router.get("/", response_model=list[LinkUrlDomainReadSerializerV2])
def link_url_domains_list_all(
        db: Session = fa.Depends(get_session_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    if not current_user.is_head:
        raise UnauthorizedException

    link_url_domains = db.query(LinkUrlDomainModel).all()
    return link_url_domains


@router.put("/{id}", response_model=LinkUrlDomainReadSerializerV2)
async def link_url_domains_update(
        id: int,
        link_url_domain_ser: LinkUrlDomainUpdateSerializerV2,
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        db: Session = fa.Depends(get_session_dependency)
):
    if not current_user.is_head:
        raise UnauthorizedException

    link_url_domain = get(db, LinkUrlDomainModel, id=id)
    if link_url_domain is None:
        raise fa.HTTPException(status_code=404, detail="project not found")

    link_url_domain = update(db, link_url_domain, link_url_domain_ser)
    return link_url_domain
