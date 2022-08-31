import fastapi as fa
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from core.dependencies import (get_db_dependency, get_current_user_dependency, period_params_dependency,
                               link_params_dependency_v2, pagination_params_dependency_v2)
from core.enums import LinkOrderByEnum, OrderEnum
from core.shared import filter_query_by_period_params, filter_query_by_link_params, paginate_query
from database.models.link import LinkModel
from database.models.user import UserModel
from database.schemas.link import (LinkReadLinkcheckLastAndDomainsSerializer,
                                   LinkReadManyTotalCountResponseModel)

router = fa.APIRouter()


@router.get("/my",
            response_model=LinkReadManyTotalCountResponseModel
            )
def links_list_my(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        db: Session = fa.Depends(get_db_dependency),
        links_order_by: LinkOrderByEnum = LinkOrderByEnum.created_at,
        links_order: OrderEnum = OrderEnum.desc,
        period_params: dict = fa.Depends(period_params_dependency),
        links_params: dict = fa.Depends(link_params_dependency_v2),
        links_pagination_params: dict = fa.Depends(pagination_params_dependency_v2),
):
    """
    get links of current user
    """

    links_query = db.query(LinkModel).filter_by(user=current_user)
    links_query = filter_query_by_period_params(links_query, period_params)
    links_query = filter_query_by_link_params(links_query, links_params, LinkModel)
    total_links_count = links_query.count()
    links_query = paginate_query(LinkModel, links_query, links_order_by, links_order, links_pagination_params)
    links = links_query.all()
    link_ser_out_list = [LinkReadLinkcheckLastAndDomainsSerializer.from_orm(link) for link in links]
    link_ser_out_list_json = jsonable_encoder(link_ser_out_list)
    return JSONResponse(content={"links": link_ser_out_list_json, "total_links_count": total_links_count})


@router.get("/my-and-my-linkbuilders",
            response_model=LinkReadManyTotalCountResponseModel
            )
def links_list_my_and_my_linkbuilders(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        db: Session = fa.Depends(get_db_dependency),
        links_order_by: LinkOrderByEnum = LinkOrderByEnum.created_at,
        links_order: OrderEnum = OrderEnum.desc,
        period_params: dict = fa.Depends(period_params_dependency),
        links_params: dict = fa.Depends(link_params_dependency_v2),
        links_pagination_params: dict = fa.Depends(pagination_params_dependency_v2),
):
    """
    get links of teamlead and his linkbuilders
    """
    if not current_user.is_teamlead:
        raise fa.HTTPException(status_code=fa.status.HTTP_401_UNAUTHORIZED,
                               detail='Only teamlead user can view other users links')
    users_id_to_view_list = [linkbuilder.id for linkbuilder in current_user.linkbuilders] + [
        current_user.id]

    links_query = db.query(LinkModel).filter(LinkModel.user_id.in_(users_id_to_view_list))

    links_query = filter_query_by_period_params(links_query, period_params)
    links_query = filter_query_by_link_params(links_query, links_params, LinkModel)
    total_links_count = links_query.count()
    links_query = paginate_query(LinkModel, links_query, links_order_by, links_order, links_pagination_params)
    links = links_query.all()
    link_ser_out_list = [LinkReadLinkcheckLastAndDomainsSerializer.from_orm(link) for link in links]
    link_ser_out_list_json = jsonable_encoder(link_ser_out_list)
    return JSONResponse(content={"links": link_ser_out_list_json, "total_links_count": total_links_count})


@router.get("/all",
            response_model=LinkReadManyTotalCountResponseModel
            )
def links_list_all(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        db: Session = fa.Depends(get_db_dependency),
        links_order_by: LinkOrderByEnum = LinkOrderByEnum.created_at,
        links_order: OrderEnum = OrderEnum.desc,
        period_params: dict = fa.Depends(period_params_dependency),
        links_params: dict = fa.Depends(link_params_dependency_v2),
        links_pagination_params: dict = fa.Depends(pagination_params_dependency_v2),
):
    """
    get all links
    """
    if not current_user.is_head:
        raise fa.HTTPException(status_code=fa.status.HTTP_401_UNAUTHORIZED,
                               detail='Only head user can view all links')
    links_query = db.query(LinkModel)

    links_query = filter_query_by_period_params(links_query, period_params)
    links_query = filter_query_by_link_params(links_query, links_params, LinkModel)
    total_links_count = links_query.count()
    links_query = paginate_query(LinkModel, links_query, links_order_by, links_order, links_pagination_params)
    links = links_query.all()
    link_ser_out_list = [LinkReadLinkcheckLastAndDomainsSerializer.from_orm(link) for link in links]
    link_ser_out_list_json = jsonable_encoder(link_ser_out_list)
    return JSONResponse(content={"links": link_ser_out_list_json, "total_links_count": total_links_count})
