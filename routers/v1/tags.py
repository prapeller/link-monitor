import fastapi as fa

from core.dependencies import (
    get_sqlalchemy_repo_dependency
)
from database.models.tag import TagModel
from database.repository import SqlAlchemyRepository
from database.schemas.tag import TagReadSerializer, TagCreateSerializer

router = fa.APIRouter()


@router.get("/",
            response_model=list[TagReadSerializer]
            )
async def tags_list(
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
):
    tags = repo.get_all(TagModel)
    return tags


@router.get("/{tag_id}",
            response_model=TagReadSerializer
            )
def tags_read(
        tag_id: int = fa.Path(...),
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
):
    """
    get tag by id
    """
    tag = repo.get(TagModel, id=tag_id)
    return tag


@router.post("/", response_model=TagReadSerializer)
async def tags_create(
        tag_ser: TagCreateSerializer,
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
):
    tag = repo.get_or_create(TagModel, tag_ser)
    return tag


@router.delete("/{tag_id}")
async def tags_delete(
        tag_id: int,
        repo: SqlAlchemyRepository = fa.Depends(get_sqlalchemy_repo_dependency),
):
    repo.remove(TagModel, id=tag_id)
    return {'message': 'ok'}
