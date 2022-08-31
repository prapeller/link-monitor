import fastapi as fa
import sqlalchemy as sa
from fastapi import UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
from sqlalchemy import String
from sqlalchemy import extract
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, Query
from sqlalchemy.sql.expression import cast

from celery_tasks import (check_link_by_id,
                          check_links_from_list,
                          check_links_all,
                          create_links_from_uploaded_file_archive,
                          check_links_per_year, check_links_from_list_playwright,
                          set_link_check_last_ids)
from core.dependencies import (get_db_dependency, get_current_user_dependency, link_params_dependency_v1,
                               pagination_params_dependency)
from core.enums import LinkOrderByEnum, OrderEnum
from core.exceptions import NotExcelException, LinkAlreadyExistsFromFileException, LinkAlreadyExistsException
from database import Base
from database.crud import (get, create, update, remove, get_or_create_many)
from database.models.link import LinkModel
from database.models.user import UserModel
from database.schemas.link import (LinkUpdateSerializer, LinkCreateSerializer,
                                   LinkReadLinkcheckLastAndDomainsSerializer,
                                   LinkReadLclDomainsUserSerializer, LinkReadManyTotalCountResponseModel,
                                   LinkReadSingleTaskIdResponseModel, LinkReadMessageTaskIdResponseModel,
                                   LinkReadManyTaskIdResponseModel, LinkReadTaskIdResponseModel,
                                   LinkReadMessageResponseModel)
from services.file_handler import iterfile, get_link_create_ser_list_from_file
from core.shared import update_domains

router = fa.APIRouter()


def filter_query(Model, query: Query, filter_params: dict) -> Query:
    for attr, value in filter_params.items():
        if attr == 'user_id' and value is not None:
            query = query.filter(getattr(Model, attr) == value)
        elif value is not None:
            query = query.filter(cast(getattr(Model, attr), String).like(f'%{filter_params[attr]}%'))
    return query


def paginate_query(Model: Base, query: Query, order_by: LinkOrderByEnum, order: OrderEnum, pagination_params) -> Query:
    order = sa.desc if order.value == 'desc' else sa.asc
    query = query.order_by(order(getattr(Model, order_by))).offset(pagination_params["offset"]).limit(
        pagination_params["limit"])
    return query


@router.get("/my",
            response_model=LinkReadManyTotalCountResponseModel
            )
def links_list_my(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        db: Session = fa.Depends(get_db_dependency),
        links_filter_params: dict = fa.Depends(link_params_dependency_v1),
        links_order_by: LinkOrderByEnum = LinkOrderByEnum.created_at,
        links_order: OrderEnum = OrderEnum.desc,
        links_pagination_params: dict = fa.Depends(pagination_params_dependency),
):
    """
    get links of current user
    """

    links_query = db.query(LinkModel) \
        .filter_by(user=current_user) \
        .filter(extract('year', LinkModel.created_at) == links_pagination_params['year'])

    links_query = filter_query(LinkModel, links_query, links_filter_params)
    total_links_count = links_query.count()
    links_query = paginate_query(LinkModel, links_query, links_order_by, links_order, links_pagination_params)
    links = links_query.all()
    link_ser_out_list = [LinkReadLinkcheckLastAndDomainsSerializer.from_orm(link) for link in links]
    link_ser_out_list_json = jsonable_encoder(link_ser_out_list)
    return JSONResponse(content={"links": link_ser_out_list_json, "total_links_count": total_links_count})


@router.get("/my-linkbuilders-links",
            response_model=LinkReadManyTotalCountResponseModel
            )
def links_list_my_linkbuilders(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        db: Session = fa.Depends(get_db_dependency),
        links_filter_params: dict = fa.Depends(link_params_dependency_v1),
        links_order_by: LinkOrderByEnum = LinkOrderByEnum.created_at,
        links_order: OrderEnum = OrderEnum.desc,
        links_pagination_params: dict = fa.Depends(pagination_params_dependency),
):
    """
    get links of teamlead's linkbuilders
    """
    if not current_user.is_teamlead:
        raise fa.HTTPException(status_code=fa.status.HTTP_401_UNAUTHORIZED,
                               detail='Only teamlead user can view other users links')
    users_id_to_view_list = [linkbuilder.id for linkbuilder in current_user.linkbuilders] + [
        current_user.id]

    links_query = db.query(LinkModel) \
        .filter(LinkModel.user_id.in_(users_id_to_view_list)) \
        .filter(extract('year', LinkModel.created_at) == links_pagination_params['year'])

    links_query = filter_query(LinkModel, links_query, links_filter_params)
    total_links_count = links_query.count()
    links_query = paginate_query(LinkModel, links_query, links_order_by, links_order, links_pagination_params)
    links = links_query.all()
    link_ser_out_list = [LinkReadLinkcheckLastAndDomainsSerializer.from_orm(link) for link in links]
    link_ser_out_list_json = jsonable_encoder(link_ser_out_list)
    return JSONResponse(content={"links": link_ser_out_list_json, "total_links_count": total_links_count})


@router.get("/get-link-upload-template")
def get_link_upload_template():
    """
    get template file for creating links
    """
    filepath = 'static/links/links_upload_template.xlsx'
    return StreamingResponse(iterfile(filepath=filepath))


@router.get("/{link_id}",
            response_model=LinkReadLclDomainsUserSerializer
            )
def links_read(
        link_id: int,
        db: Session = fa.Depends(get_db_dependency),
):
    """
    get link by id
    """
    link = get(db, LinkModel, id=link_id)
    if link is None:
        raise fa.HTTPException(status_code=404, detail="Link not found")
    return link


@router.get("/",
            response_model=LinkReadManyTotalCountResponseModel
            )
def links_list(
        db: Session = fa.Depends(get_db_dependency),
        links_filter_params: dict = fa.Depends(link_params_dependency_v1),
        links_order_by: LinkOrderByEnum = LinkOrderByEnum.created_at,
        links_order: OrderEnum = OrderEnum.desc,
        links_pagination_params: dict = fa.Depends(pagination_params_dependency),
):
    """
    get all links
    """

    links_query = db.query(LinkModel) \
        .filter(extract('year', LinkModel.created_at) == links_pagination_params['year'])

    links_query = filter_query(LinkModel, links_query, links_filter_params)
    total_links_count = links_query.count()
    links_query = paginate_query(LinkModel, links_query, links_order_by, links_order, links_pagination_params)
    links = links_query.all()
    link_ser_out_list = [LinkReadLinkcheckLastAndDomainsSerializer.from_orm(link) for link in links]
    link_ser_out_list_json = jsonable_encoder(link_ser_out_list)
    return JSONResponse(content={"links": link_ser_out_list_json, "total_links_count": total_links_count})


@router.put("/{link_id}",
            response_model=LinkReadSingleTaskIdResponseModel
            )
async def links_update(
        link_id: int,
        link_ser: LinkUpdateSerializer,
        db: Session = fa.Depends(get_db_dependency),
):
    """
    update link by id
    and run its checking in background
    """
    link = get(db, LinkModel, id=link_id)
    if link is None:
        raise fa.HTTPException(status_code=404, detail="Link not found")
    try:
        link = update(db, link, link_ser)
    except IntegrityError as error:
        raise LinkAlreadyExistsException(error)
    update_domains(db, link)

    task = check_link_by_id.delay(id=link_id)
    link_ser_out = LinkReadLinkcheckLastAndDomainsSerializer.from_orm(link)
    link_ser_out_json = jsonable_encoder(link_ser_out)
    return JSONResponse(content={"link": link_ser_out_json, "task_id": task.task_id})


@router.post("/my",
             response_model=LinkReadSingleTaskIdResponseModel
             )
async def links_create_my(
        link_ser: LinkCreateSerializer,
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        db: Session = fa.Depends(get_db_dependency),
):
    """
    create link of current user
    and run its checking in background
    """
    link = get(db, LinkModel,
               page_url=link_ser.page_url, anchor=link_ser.anchor, link_url=link_ser.link_url)
    if link:
        raise LinkAlreadyExistsException(link)
    link_ser.user_id = current_user.id
    link = create(db, LinkModel, link_ser)

    task = check_link_by_id.delay(id=link.id)
    link_ser_out = LinkReadLinkcheckLastAndDomainsSerializer.from_orm(link)
    link_ser_out_json = jsonable_encoder(link_ser_out)
    return JSONResponse(content={"link": link_ser_out_json, "task_id": task.task_id})


@router.post("/check-my",
             status_code=fa.status.HTTP_201_CREATED)
def tasks_check_links_my(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        db: Session = fa.Depends(get_db_dependency),
):
    links = db.query(LinkModel).filter_by(user=current_user)
    links_id_list = [link.id for link in links]
    task = check_links_from_list.delay(id_list=links_id_list)
    return {'task_id': f'{task.task_id}'}


@router.post("/set-link-check-last-ids/all",
             status_code=fa.status.HTTP_201_CREATED)
def tasks_set_link_check_last_ids(
        db: Session = fa.Depends(get_db_dependency),
):
    links = db.query(LinkModel).all()
    links_id_list = [link.id for link in links]
    task = set_link_check_last_ids.delay(id_list=links_id_list)
    return {'task_id': f'{task.task_id}'}


@router.post("/check-year",
             status_code=fa.status.HTTP_201_CREATED,
             )
def tasks_check_links_all_async(
        year: int = fa.Body(...),
):
    task = check_links_per_year.delay(year=year)
    return {'task_id': f'{task.task_id}'}


@router.post("/check-many",
             response_model=LinkReadMessageTaskIdResponseModel,
             )
async def links_check_many(
        link_id_list: list[int] = fa.Body(...),
):
    """
    run checking of many links (by link_id_list) in background
    """
    task = check_links_from_list.delay(id_list=link_id_list)
    return JSONResponse(content={'message': 'ok', "task_id": task.task_id})


@router.post("/check-all",
             status_code=fa.status.HTTP_201_CREATED,
             )
async def links_check_all_async():
    task = check_links_all.delay()
    return {'task_id': f'{task.task_id}'}


@router.post("/check-many/mode/none/sync",
             status_code=fa.status.HTTP_201_CREATED)
def tasks_check_links_all_sync(
        link_id_list: list[int] = fa.Body(...),
):
    check_links_from_list(id_list=link_id_list)
    return {'message': 'ok'}


@router.post("/check-many/mode/playwright/sync",
             status_code=fa.status.HTTP_201_CREATED)
def tasks_check_links_all_sync(
        link_id_list: list[int] = fa.Body(...),
):
    check_links_from_list_playwright(id_list=link_id_list)
    return {'message': 'ok'}


@router.post("/check-all/sync",
             status_code=fa.status.HTTP_201_CREATED,
             )
def links_check_all_sync():
    check_links_all()
    return {'message': 'ok'}


@router.post("/my/upload-from-file",
             response_model=LinkReadManyTaskIdResponseModel
             )
async def links_create_my_from_file(
        file: UploadFile,
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        db: Session = fa.Depends(get_db_dependency),
):
    """
    create links from template .xlsx file
    and run their checking in background
    """
    if file.content_type != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        raise NotExcelException
    uploaded_file_path = f'static/report/uploaded_links_file_by_user_id_{current_user.id}.xlsx'
    contents = await file.read()
    with open(uploaded_file_path, 'wb') as uploaded:
        uploaded.write(contents)

    link_create_ser_list = get_link_create_ser_list_from_file(filepath=uploaded_file_path,
                                                              current_user_id=current_user.id)
    try:
        links = get_or_create_many(db, LinkModel, link_create_ser_list)
    except IntegrityError as error:
        raise LinkAlreadyExistsFromFileException(filepath=uploaded_file_path, error=error)

    links_id_list = [str(link.id) for link in links]

    task = check_links_from_list.delay(id_list=links_id_list)
    link_ser_out_list = [LinkReadLinkcheckLastAndDomainsSerializer.from_orm(link) for link in links]
    link_ser_out_list_json = jsonable_encoder(link_ser_out_list)
    return JSONResponse(content={"links": link_ser_out_list_json, "task_id": task.task_id})


@router.post("/upload-from-file-archive-sync",
             response_model=LinkReadTaskIdResponseModel
             )
async def links_create_from_file_archive(
        file: UploadFile,
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    """
    create links from .xlsx archive file
    and run their checking in background
    """
    if file.content_type != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        raise NotExcelException
    uploaded_file_path = f'static/report/uploaded_links_archive_by_user_id_{current_user.id}.xlsx'
    contents = await file.read()
    with open(uploaded_file_path, 'wb') as uploaded:
        uploaded.write(contents)

    create_links_from_uploaded_file_archive(uploaded_file_path=uploaded_file_path,
                                            current_user_id=current_user.id)
    return {'message': 'ok'}


@router.post("/upload-from-file-archive",
             response_model=LinkReadTaskIdResponseModel
             )
async def links_create_from_file_archive(
        file: UploadFile,
        current_user: UserModel = fa.Depends(get_current_user_dependency),
):
    """
    create links from .xlsx archive file
    and run their checking in background
    """
    if file.content_type != 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        raise NotExcelException
    uploaded_file_path = f'static/report/uploaded_links_archive_by_user_id_{current_user.id}.xlsx'
    contents = await file.read()
    with open(uploaded_file_path, 'wb') as uploaded:
        uploaded.write(contents)

    task = create_links_from_uploaded_file_archive.delay(uploaded_file_path=uploaded_file_path,
                                                         current_user_id=current_user.id)
    return JSONResponse(content={"task_id": task.task_id})


@router.delete("/many",
               response_model=LinkReadMessageResponseModel)
async def links_delete_many(
        link_id_list: list[int] = fa.Body(...),
        db: Session = fa.Depends(get_db_dependency),
):
    """
    delete many link from id_list
    """
    for link_id in link_id_list:
        remove(db, LinkModel, link_id)
    return {'message': 'ok'}


@router.delete("/{link_id}",
               response_model=LinkReadMessageResponseModel)
async def links_delete(
        link_id: int,
        db: Session = fa.Depends(get_db_dependency),
):
    """
    delete link
    """
    link = get(db, LinkModel, id=link_id)
    if link is None:
        raise fa.HTTPException(status_code=404, detail="Link not found")
    remove(db, LinkModel, link_id)
    return {'message': 'ok'}
