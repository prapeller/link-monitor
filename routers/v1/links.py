from typing import Union

import fastapi as fa
from fastapi import UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.config import settings
from core.dependencies import (
    get_session_dependency,
    get_current_user_dependency,
    get_current_user_roles_dependency,
    period_params_dependency,
    link_params_dependency,
    pagination_params_dependency
)
from core.enums import (
    LinkOrderByEnum,
    OrderEnum,
    StartModeEnum
)
from core.exceptions import (
    NotExcelException,
    LinkAlreadyExistsFromFileException,
    LinkAlreadyExistsException
)
from core.exceptions import UnauthorizedException
from core.shared import (
    filter_query_by_period_params_link,
    filter_query_by_model_params_link,
    paginate_query, chunks_generator
)
from database.crud import (get, create, update, remove, get_or_create_many)
from database.models.link import LinkModel
from database.models.user import UserModel
from database.schemas.link import (
    LinkUpdateSerializer,
    LinkCreateSerializer,
    LinkReadLinkcheckLastAndDomainsSerializer,
    LinkReadLclDomainsUserSerializer,
    LinkReadSingleTaskIdResponseModel,
    LinkReadMessageTaskIdResponseModel,
    LinkReadManyTaskIdResponseModel,
    LinkReadTaskIdResponseModel,
    LinkReadManyTotalCountResponseModel
)
from services.file_handler.file_handler import (
    iterfile,
    get_link_create_ser_list_from_file,
    create_links_from_uploaded_file_archive
)
from services.link_checker.link_checker import (
    LinkChecker
)
from services.link_checker.celery_tasks import (
    check_link_by_id,
    check_links_from_list,
    check_links_all,
    check_links_from_list_playwright,
    check_links_per_year,
    check_every_day
)

router = fa.APIRouter()


@router.get(
    "/get-link-upload-template",
    status_code=fa.status.HTTP_200_OK,
)
def get_link_upload_template():
    """
    get template file for creating links
    """
    filepath = 'static/links/links_upload_template.xlsx'
    return StreamingResponse(iterfile(filepath=filepath))


@router.get(
    "/my-seo",
    response_model=LinkReadManyTotalCountResponseModel,
    status_code=fa.status.HTTP_200_OK,
)
def links_list_my_seo(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        current_user_roles: UserModel = fa.Depends(get_current_user_roles_dependency),
        db: Session = fa.Depends(get_session_dependency),
        links_order_by: LinkOrderByEnum = LinkOrderByEnum.created_at,
        links_order: OrderEnum = OrderEnum.desc,
        period_params: dict = fa.Depends(period_params_dependency),
        links_params: dict = fa.Depends(link_params_dependency),
        links_pagination_params: dict = fa.Depends(pagination_params_dependency),
):
    """
    get links of projects that current seo user has access to
    """
    if not 'seo' in current_user_roles:
        raise fa.HTTPException(status_code=fa.status.HTTP_401_UNAUTHORIZED,
                               detail='Only seo user can view seo links')
    links_query = db.query(LinkModel) \
        .filter(LinkModel.link_url_domain_id.in_(current_user.seo_link_url_domains_id))
    total_links_count = links_query.count()
    links_query = filter_query_by_period_params_link(links_query, period_params)
    links_query = filter_query_by_model_params_link(links_query, links_params)
    filtered_links_count = links_query.count()
    links_query = paginate_query(LinkModel, links_query, links_order_by, links_order, links_pagination_params)
    links = links_query.all()
    link_ser_out_list = [LinkReadLinkcheckLastAndDomainsSerializer.from_orm(link) for link in links]
    link_ser_out_list_json = jsonable_encoder(link_ser_out_list)
    return JSONResponse(content={'links': link_ser_out_list_json,
                                 'total_links_count': total_links_count,
                                 'filtered_links_count': filtered_links_count})


@router.get(
    "/my",
    response_model=LinkReadManyTotalCountResponseModel,
    status_code=fa.status.HTTP_200_OK,
)
def links_list_my(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        db: Session = fa.Depends(get_session_dependency),
        links_order_by: LinkOrderByEnum = LinkOrderByEnum.created_at,
        links_order: OrderEnum = OrderEnum.desc,
        period_params: dict = fa.Depends(period_params_dependency),
        links_params: dict = fa.Depends(link_params_dependency),
        links_pagination_params: dict = fa.Depends(pagination_params_dependency),
):
    """
    get links of current user
    """

    links_query = db.query(LinkModel).filter_by(user=current_user)
    total_links_count = links_query.count()
    links_query = filter_query_by_period_params_link(links_query, period_params)
    links_query = filter_query_by_model_params_link(links_query, links_params)
    filtered_links_count = links_query.count()
    links_query = paginate_query(LinkModel, links_query, links_order_by, links_order, links_pagination_params)
    links = links_query.all()
    link_ser_out_list = [LinkReadLinkcheckLastAndDomainsSerializer.from_orm(link) for link in links]
    link_ser_out_list_json = jsonable_encoder(link_ser_out_list)
    return JSONResponse(content={'links': link_ser_out_list_json,
                                 'total_links_count': total_links_count,
                                 'filtered_links_count': filtered_links_count})


@router.get(
    "/my-and-my-linkbuilders",
    response_model=LinkReadManyTotalCountResponseModel,
    status_code=fa.status.HTTP_200_OK,
)
def links_list_my_and_my_linkbuilders(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        db: Session = fa.Depends(get_session_dependency),
        links_order_by: LinkOrderByEnum = LinkOrderByEnum.created_at,
        links_order: OrderEnum = OrderEnum.desc,
        period_params: dict = fa.Depends(period_params_dependency),
        links_params: dict = fa.Depends(link_params_dependency),
        links_pagination_params: dict = fa.Depends(pagination_params_dependency),
):
    """
    get links of teamlead and his linkbuilders
    """
    if not current_user.is_teamlead:
        raise UnauthorizedException

    users_id_to_view_list = [linkbuilder.id for linkbuilder in current_user.linkbuilders] + [
        current_user.id]

    links_query = db.query(LinkModel).filter(LinkModel.user_id.in_(users_id_to_view_list))
    total_links_count = links_query.count()
    links_query = filter_query_by_period_params_link(links_query, period_params)
    links_query = filter_query_by_model_params_link(links_query, links_params)
    filtered_links_count = links_query.count()
    links_query = paginate_query(LinkModel, links_query, links_order_by, links_order, links_pagination_params)
    links = links_query.all()
    link_ser_out_list = [LinkReadLinkcheckLastAndDomainsSerializer.from_orm(link) for link in links]
    link_ser_out_list_json = jsonable_encoder(link_ser_out_list)
    return JSONResponse(content={'links': link_ser_out_list_json,
                                 'total_links_count': total_links_count,
                                 'filtered_links_count': filtered_links_count})


@router.get(
    "/all",
    response_model=LinkReadManyTotalCountResponseModel,
    status_code=fa.status.HTTP_200_OK,
)
def links_list_all(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        db: Session = fa.Depends(get_session_dependency),
        links_order_by: LinkOrderByEnum = LinkOrderByEnum.created_at,
        links_order: OrderEnum = OrderEnum.desc,
        period_params: dict = fa.Depends(period_params_dependency),
        links_params: dict = fa.Depends(link_params_dependency),
        links_pagination_params: dict = fa.Depends(pagination_params_dependency),
):
    """
    get all links
    """
    if not current_user.is_head:
        raise UnauthorizedException

    links_query = db.query(LinkModel)
    total_links_count = links_query.count()
    links_query = filter_query_by_period_params_link(links_query, period_params)
    links_query = filter_query_by_model_params_link(links_query, links_params)
    filtered_links_count = links_query.count()
    links_query = paginate_query(LinkModel, links_query, links_order_by, links_order, links_pagination_params)
    links = links_query.all()
    link_ser_out_list = [LinkReadLinkcheckLastAndDomainsSerializer.from_orm(link) for link in links]
    link_ser_out_list_json = jsonable_encoder(link_ser_out_list)
    return JSONResponse(content={'links': link_ser_out_list_json,
                                 'total_links_count': total_links_count,
                                 'filtered_links_count': filtered_links_count})


@router.get(
    "/{link_id}",
    response_model=LinkReadLclDomainsUserSerializer,
    status_code=fa.status.HTTP_200_OK,
)
def links_read(
        link_id: int,
        db: Session = fa.Depends(get_session_dependency),
):
    """
    get link by id
    """
    link = get(db, LinkModel, id=link_id)
    if link is None:
        raise fa.HTTPException(status_code=404, detail="Link not found")
    return link


@router.put(
    "/{link_id}",
    response_model=LinkReadSingleTaskIdResponseModel,
    status_code=fa.status.HTTP_202_ACCEPTED,
)
async def links_update(
        link_id: int,
        link_ser: LinkUpdateSerializer,
        session: Session = fa.Depends(get_session_dependency),
):
    """
    update link by id
    and run its checking in background
    """
    link = get(session, LinkModel, id=link_id)
    if link is None:
        raise fa.HTTPException(status_code=404, detail="Link not found")
    try:
        link = update(session, link, link_ser)
    except IntegrityError as error:
        raise LinkAlreadyExistsException(error)

    task = check_link_by_id.delay(id=link_id)
    link_ser_out = LinkReadLinkcheckLastAndDomainsSerializer.from_orm(link)
    link_ser_out_json = jsonable_encoder(link_ser_out)
    return JSONResponse(content={"link": link_ser_out_json, "task_id": task.task_id})


@router.post(
    "/my",
    response_model=LinkReadSingleTaskIdResponseModel,
    status_code=fa.status.HTTP_201_CREATED,
)
async def links_create_my(
        link_ser: LinkCreateSerializer,
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        db: Session = fa.Depends(get_session_dependency),
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


@router.post(
    "/check-my",
    status_code=fa.status.HTTP_201_CREATED,
)
def tasks_check_links_my(
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        db: Session = fa.Depends(get_session_dependency),
):
    links = db.query(LinkModel).filter_by(user=current_user)
    links_id_list = [link.id for link in links]
    task = check_links_from_list.delay(id_list=links_id_list)
    return {'task_id': f'{task.task_id}'}


@router.post(
    "/check-year",
    status_code=fa.status.HTTP_201_CREATED,
)
def links_check_all_async(
        year: int = fa.Body(...),
):
    task = check_links_per_year.delay(year=year)
    return {'task_id': f'{task.task_id}'}


@router.post(
    "/check-many",
    response_model=Union[LinkReadMessageTaskIdResponseModel, dict],
    status_code=fa.status.HTTP_201_CREATED,
)
def links_check_many(
        link_id_list: list[int] = fa.Body(...),
        sync_mode: bool = fa.Query(False),
        start_mode: StartModeEnum = fa.Query(StartModeEnum.httpx),
):
    if sync_mode:
        if start_mode == StartModeEnum.httpx:
            check_links_from_list(id_list=link_id_list)
        elif start_mode == StartModeEnum.playwright:
            check_links_from_list_playwright(id_list=link_id_list)
        return {'message': 'ok'}
    else:
        task = check_links_from_list.delay(id_list=link_id_list)
        return JSONResponse(content={'message': 'ok', "task_id": task.task_id})


@router.post(
    "/check-all",
    response_model=LinkReadMessageTaskIdResponseModel,
    status_code=fa.status.HTTP_201_CREATED,
)
def links_check_all():
    task = check_links_all.delay()
    return JSONResponse(content={'message': 'ok', "task_id": task.task_id})


@router.post(
    "/check-every-day",
    response_model=LinkReadMessageTaskIdResponseModel,
    status_code=fa.status.HTTP_201_CREATED,
)
def links_check_every_day(
        sync_mode: bool = fa.Query(False),
):
    if sync_mode:
        check_every_day()
        return {'message': 'ok'}
    else:
        task = check_every_day.delay()
        return JSONResponse(content={'message': 'ok', "task_id": task.task_id})


@router.post(
    "/my/upload-from-file",
    response_model=Union[LinkReadManyTaskIdResponseModel, dict],
    status_code=fa.status.HTTP_201_CREATED,
)
async def links_create_my_from_file(
        file: UploadFile,
        sync_mode: bool = fa.Query(default=False),
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        db: Session = fa.Depends(get_session_dependency),
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

    if links:
        if sync_mode:
            for link_chunk in chunks_generator(links, settings.LINK_CHECKER_CHUNK_SIZE):
                linkchecker = LinkChecker(db)
                print(linkchecker)
                await linkchecker.check_links(links=link_chunk)
                print(f'LINK_CHECKER_CHUNK_SIZE: {settings.LINK_CHECKER_CHUNK_SIZE}\n\n\n')
            return {'message': 'ok'}
        else:
            links_id_list = [str(link.id) for link in links]
            task = check_links_from_list.delay(id_list=links_id_list)
            link_ser_out_list = [LinkReadLinkcheckLastAndDomainsSerializer.from_orm(link) for link in links]
            link_ser_out_list_json = jsonable_encoder(link_ser_out_list)
            return JSONResponse(content={"links": link_ser_out_list_json, "task_id": task.task_id})


@router.post(
    "/upload-from-file-archive",
    response_model=LinkReadTaskIdResponseModel,
    status_code=fa.status.HTTP_201_CREATED,
)
async def links_create_from_file_archive(
        file: UploadFile,
        current_user: UserModel = fa.Depends(get_current_user_dependency),
        sync_mode: bool = fa.Body(default=False),
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

    if sync_mode:
        create_links_from_uploaded_file_archive(uploaded_file_path=uploaded_file_path,
                                                current_user_id=current_user.id)
        return {'message': 'ok'}
    else:
        task = create_links_from_uploaded_file_archive.delay(uploaded_file_path=uploaded_file_path,
                                                             current_user_id=current_user.id)
        return JSONResponse(content={"task_id": task.task_id})


@router.delete(
    "/many",
    status_code=fa.status.HTTP_204_NO_CONTENT,
)
async def links_delete_many(
        link_id_list: list[int] = fa.Body(...),
        db: Session = fa.Depends(get_session_dependency),
):
    """
    delete many link from id_list
    """
    for link_id in link_id_list:
        remove(db, LinkModel, link_id)


@router.delete(
    "/{link_id}",
    status_code=fa.status.HTTP_204_NO_CONTENT,
)
async def links_delete(
        link_id: int,
        db: Session = fa.Depends(get_session_dependency),
):
    """
    delete link
    """
    remove(db, LinkModel, link_id)
