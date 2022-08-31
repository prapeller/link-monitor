import fastapi as fa
from sqlalchemy.orm import Session

from core.dependencies import get_db_dependency, get_current_user_dependency
from database.crud import get, remove
from database.models.link_url_domain import LinkUrlDomainModel
from database.models.user import UserModel
from database.schemas.link_url_domain import LinkUrlDomainReadSerializer

router = fa.APIRouter()


@router.get("/", response_model=list[LinkUrlDomainReadSerializer], deprecated=True)
def link_url_domains_list(
        db: Session = fa.Depends(get_db_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    if not current_user.is_head:
        raise fa.HTTPException(status_code=fa.status.HTTP_401_UNAUTHORIZED,
                               detail='Only head user can view all projects')
    link_url_domains = db.query(LinkUrlDomainModel).all()
    return link_url_domains


@router.delete("/{link_url_domain_id}")
async def link_url_domains_delete(
        link_url_domain_id: int,
        db: Session = fa.Depends(get_db_dependency),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    if not current_user.is_head:
        raise fa.HTTPException(status_code=fa.status.HTTP_401_UNAUTHORIZED,
                               detail='Only head user can delete link_url_domain')
    link_url_domain = get(db, LinkUrlDomainModel, id=link_url_domain_id)
    if link_url_domain is None:
        raise fa.HTTPException(status_code=404, detail="link_url_domain not found")

    remove(db, LinkUrlDomainModel, link_url_domain_id)
    return {'message': 'ok'}
