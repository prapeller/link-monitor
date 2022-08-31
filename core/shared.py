import re
import traceback

import sqlalchemy as sa
from sqlalchemy.orm import Session, Query

from core.enums import LinkOrderByEnum, OrderEnum
from database import Base
from database.crud import get_or_create
from database.models.link import LinkModel
from database.models.link_check import LinkCheckModel
from database.models.link_url_domain import LinkUrlDomainModel
from database.models.page_url_domain import PageUrlDomainModel
from database.schemas.link_url_domain import LinkUrlDomainCreateSerializer
from database.schemas.page_url_domain import PageUrlDomainCreateSerializer


def get_link_check_last(link) -> LinkCheckModel:
    """for link - getting link.link_check_last from link.link_checks"""
    link_check_last = None
    if link.link_checks:
        link_checks_sorted = sorted(link.link_checks, key=lambda x: x.id)
        link_check_last = link_checks_sorted[-1]
    return link_check_last


def set_link_check_last(link) -> None:
    """for link - setting link_check_last_id, link.link_check_last_result_message, link_check_last_status"""
    linkcheck_last = get_link_check_last(link)
    link.link_check_last_id = linkcheck_last.id if linkcheck_last else None
    link.link_check_last_result_message = linkcheck_last.result_message if linkcheck_last else None
    link.link_check_last_status = linkcheck_last.status if linkcheck_last else None


def chunks_generator(lst, chunk_size):
    """Yield chunk_sized elements chunks from lst sequence."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


def get_domain_name_from_url(page_url) -> str | None:
    try:
        match = re.search(
            pattern=r"(?:https?:)?(?:\/\/)?(?:[^@\/\n]+@)?(?:www\.)?([^:\/?\n]+\.[^:\/?\n]+)",
            string=page_url.lower()
        )
        domain_name = match.group(1) if match else ''
        return domain_name
    except Exception:
        print(traceback.format_exc())
        return None


def update_domains(db, link: LinkModel) -> None:
    page_url_domain_name = get_domain_name_from_url(link.page_url)
    page_url_domain = get_or_create(
        db, PageUrlDomainModel, PageUrlDomainCreateSerializer(name=page_url_domain_name))
    link.page_url_domain = page_url_domain

    link_url_domain_name = get_domain_name_from_url(link.link_url)
    link_url_domain = get_or_create(
        db, LinkUrlDomainModel, LinkUrlDomainCreateSerializer(name=link_url_domain_name))
    link.link_url_domain = link_url_domain

    db.commit()
    db.refresh(link)


def normalize(string: str) -> str:
    string = string.lower() \
        .replace('\n', ' ') \
        .replace(' ', ' ') \
        .replace("'", '') \
        .replace("’", '') \
        .strip() \
        .strip('/')
    string = re.sub(pattern=r"(\s)+", repl=' ', string=string)
    return string


def check_if_link_domains_exist(db: Session, link: LinkModel) -> None:
    if not link.page_url_domain:
        page_url_domain_name = get_domain_name_from_url(link.page_url)
        page_url_domain = get_or_create(
            db, PageUrlDomainModel, PageUrlDomainCreateSerializer(name=page_url_domain_name))
        link.page_url_domain = page_url_domain
        db.commit()

    if not link.link_url_domain:
        link_url_domain_name = get_domain_name_from_url(link.link_url)
        link_url_domain = get_or_create(
            db, LinkUrlDomainModel, LinkUrlDomainCreateSerializer(name=link_url_domain_name))
        link.link_url_domain = link_url_domain
        db.commit()


def remove_https(link_url) -> str:
    return link_url.replace('https:', '')


def filter_query_by_period_params(query: Query, filter_params: dict) -> Query:
    date_from = filter_params.get('date_from')
    date_upto = filter_params.get('date_upto')
    if date_from is not None and date_upto is not None:
        query = query.filter(sa.text(f"""
        created_at >= timestamp '{date_from} 00:00:01'
        and created_at <= timestamp '{date_upto} 23:59:59'
        """))
    return query


def filter_query_by_link_params(query: Query, filter_params: dict, Model: Base) -> Query:
    for attr, value in filter_params.items():
        if attr == 'link_url_domain_name' and value is not None:
            query = query.filter(sa.func.lower(getattr(Model, attr)) == value.lower())
        elif attr == 'user_id' and value is not None:
            query = query.filter(getattr(Model, attr) == value)
        elif attr == 'link_check_last_status' and value is not None:
            query = query.filter(getattr(Model, attr) == value.value)
        elif attr == 'price' and value is not None:
            query = query.filter(sa.func.cast(getattr(Model, attr), sa.String).like(f'%{str(value).lower()}%'))
        elif value is not None:
            query = query.filter(sa.func.lower(getattr(Model, attr)).like(f'%{value.lower()}%'))
    return query


def paginate_query(Model: Base, query: Query, order_by: LinkOrderByEnum, order: OrderEnum, pagination_params) -> Query:
    order = sa.desc if order.value == 'desc' else sa.asc
    query = query.order_by(order(getattr(Model, order_by))) \
        .offset(pagination_params["offset"]) \
        .limit(pagination_params["limit"])
    return query
