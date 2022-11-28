import fastapi as fa
from sqlalchemy.orm import Session

from core.dependencies import (
    get_session_dependency
)
from database.models.tag import TagModel
from database.repository import SqlAlchemyRepository
from database.schemas.tag import TagReadSerializer, TagCreateSerializer

router = fa.APIRouter()


@router.get("/",
            response_model=list[TagReadSerializer]
            )
async def tags_list(
        session: Session = fa.Depends(get_session_dependency),
):
    repo = SqlAlchemyRepository(session)
    tags = repo.get_all(TagModel)
    return tags


@router.get("/{tag_id}",
            response_model=TagReadSerializer
            )
def tags_read(
        tag_id: int = fa.Path(...),
        session: Session = fa.Depends(get_session_dependency),
):
    """
    get tag by id
    """
    repo = SqlAlchemyRepository(session)
    tag = repo.get(TagModel, id=tag_id)
    if tag is None:
        raise fa.HTTPException(status_code=404, detail="Tag not found")

    return tag


@router.post("/", response_model=TagReadSerializer)
async def tags_create(
        tag_ser: TagCreateSerializer,
        session: Session = fa.Depends(get_session_dependency),
):
    repo = SqlAlchemyRepository(session)
    tag = repo.get_or_create(TagModel, tag_ser)
    return tag


@router.delete("/{tag_id}")
async def tags_delete(
        tag_id: int,
        session: Session = fa.Depends(get_session_dependency),
):
    repo = SqlAlchemyRepository(session)
    tag = repo.get(TagModel, id=tag_id)
    if tag is None:
        raise fa.HTTPException(status_code=404, detail="tag not found")

    repo.remove(TagModel, id=tag_id)
    return {'message': 'ok'}
