import fastapi as fa
from sqlalchemy import desc
from sqlalchemy.orm import Session

from core.dependencies import get_session_dependency, get_current_user_dependency
from database.crud import get, remove
from database.models.link_check import LinkCheckModel
from database.models.user import UserModel
from database.schemas.link_check import (
    LinkCheckReadLinkSerializer, LinkCheckReadSerializer,
)

router = fa.APIRouter()


@router.get("/", response_model=list[LinkCheckReadLinkSerializer])
def linkchecks_list(
        db: Session = fa.Depends(get_session_dependency),
):
    """
    get all linkchecks
    """
    linkchecks = db.query(LinkCheckModel).order_by(desc(LinkCheckModel.id)).all()
    return linkchecks


@router.get("/my", response_model=list[LinkCheckReadLinkSerializer])
def linkchecks_list_my(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        db: Session = fa.Depends(get_session_dependency),
):
    """"
    get all linkchecks of current user
    """
    linkchecks = db.query(LinkCheckModel).filter(
        LinkCheckModel.link.has(user=current_user)).order_by(desc(LinkCheckModel.id)).all()
    return linkchecks


@router.get("/{linkcheck_id}", response_model=LinkCheckReadLinkSerializer)
def linkchecks_read(
        linkcheck_id: int,
        db: Session = fa.Depends(get_session_dependency),
):
    """
    get linkcheck by id
    """
    linkcheck = get(db, LinkCheckModel, id=linkcheck_id)
    if linkcheck is None:
        raise fa.HTTPException(status_code=404, detail="Linkcheck not found")
    return linkcheck


@router.get("/link/{link_id}", response_model=list[LinkCheckReadSerializer])
def linkchecks_list_by_link(
        link_id: int,
        db: Session = fa.Depends(get_session_dependency),
):
    """
    get linkchecks of link
    """
    linkchecks = db.query(LinkCheckModel).filter(
        LinkCheckModel.link.has(id=link_id)).order_by(desc(LinkCheckModel.id)).all()
    return linkchecks


@router.delete("/{linkcheck_id}")
async def linkchecks_delete(
        linkcheck_id: int,
        db: Session = fa.Depends(get_session_dependency),
):
    """
    delete linkcheck
    """
    remove(db, LinkCheckModel, linkcheck_id)
    return {'message': 'ok'}
