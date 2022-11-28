import fastapi as fa
from sqlalchemy.orm import Session

from core.dependencies import get_session_dependency, get_current_user_dependency
from core.exceptions import UnauthorizedException
from database.crud import get, remove
from database.models.link_url_domain import LinkUrlDomainModel
from database.models.user import UserModel
from database.schemas.link_url_domain import LinkUrlDomainReadSerializer

router = fa.APIRouter()


@router.get("/", response_model=list[LinkUrlDomainReadSerializer], deprecated=True)
def link_url_domains_list(
        db: Session = fa.Depends(get_session_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    if not current_user.is_head:
        raise UnauthorizedException

    link_url_domains = db.query(LinkUrlDomainModel).all()
    return link_url_domains


@router.delete("/{link_url_domain_id}")
async def link_url_domains_delete(
        link_url_domain_id: int,
        db: Session = fa.Depends(get_session_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    if not current_user.is_head:
        raise UnauthorizedException

    remove(db, LinkUrlDomainModel, link_url_domain_id)
    return {'message': 'ok'}
