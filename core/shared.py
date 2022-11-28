import re
from collections import OrderedDict

import httpx
import sqlalchemy as sa
from sqlalchemy.orm import Session, Query
from sqlalchemy.sql import and_

from core.enums import OrderEnum
from database import Base
from database.models.link import LinkModel
from database.models.link_check import LinkCheckModel
from database.models.page_url_domain import PageUrlDomainModel


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


def normalize(string: str) -> str:
    """
    re.sub for:

    - any space character to ' '
    - any ending line non-alphabetic character to ''
    """
    string = string.lower() \
        .replace('\n', ' ') \
        .replace(' ', ' ') \
        .replace("'", '') \
        .replace("’", '') \
        .replace("­", '') \
        .replace("–", '-') \
        .strip('/') \
        .strip()
    string = re.sub(pattern=r"(\s)+", repl=' ', string=string)
    string = re.sub(pattern=r"[^a-zA-Z]+$", repl='', string=string)
    return string


def remove_https(link_url) -> str:
    return link_url.replace('https:', '')


def filter_query_by_period_params_link(query: Query, filter_params: dict) -> Query:
    """filter by link period (link.created_at)"""
    date_from = filter_params.get('date_from')
    date_upto = filter_params.get('date_upto')
    if date_from is not None and date_upto is not None:
        query = query.filter(sa.text(f"""
        link.created_at >= timestamp '{date_from} 00:00:00'
        and link.created_at <= timestamp '{date_upto} 23:59:59'
        """))
    return query


def filter_query_by_period_params_pudomain_link(query: Query, filter_params: dict) -> Query:
    """filter by domain's last link period (page_url_domain.link_created_at_last"""
    date_from = filter_params.get('date_from')
    date_upto = filter_params.get('date_upto')
    if date_from is not None and date_upto is not None:
        query = query \
            .filter(and_(
            sa.func.date(PageUrlDomainModel.link_created_at_last) >= date_from,
            sa.func.date(PageUrlDomainModel.link_created_at_last) <= date_upto))
    return query


def filter_query_by_model_params_link(query: Query, filter_params: dict) -> Query:
    for attr, value in filter_params.items():

        # filter by link.link_url_domain.name params:
        # if client send query_params '&link_url_domain_name=20bet.tv&link_url_domain_name=20-bet.in'
        # then will be interpreted to filter_params['link_url_domain_name'] = ['20bet.tv', '20-bet.in']
        if attr == 'link_url_domain_name' and value is not None:
            query = query.filter(sa.func.lower(LinkModel.link_url_domain_name).in_([l.lower() for l in value]))

        # filter by user
        elif attr == 'user_id' and value is not None:
            query = query.filter(LinkModel.user_id == value)

        # filter by status of last linkcheck
        elif attr == 'link_check_last_status' and value is not None:
            query = query.filter(LinkModel.link_check_last_status == value.value)

        # filter by price
        elif attr == 'price' and value is not None:
            query = query.filter(sa.func.cast(LinkModel.price, sa.String).like(f'%{str(value).lower()}%'))

        # other filter_params
        elif value is not None:
            query = query.filter(sa.func.lower(getattr(LinkModel, attr)).like(f'%{value.lower()}%'))
    return query


def filter_query_by_model_params_pudomain(query: Query, filter_params: dict) -> Query:
    for attr, value in filter_params.items():

        if attr == 'name' and value is not None:
            query = query.filter(sa.func.lower(PageUrlDomainModel.name).like(f'%{value.lower()}%'))

        elif attr == 'link_da_last_from' and value is not None:
            query = query.filter(sa.func.cast(PageUrlDomainModel.link_da_last, sa.Float) >= value)
        elif attr == 'link_da_last_upto' and value is not None:
            query = query.filter(sa.func.cast(PageUrlDomainModel.link_da_last, sa.Float) <= value)

        elif attr == 'link_dr_last_from' and value is not None:
            query = query.filter(sa.func.cast(PageUrlDomainModel.link_dr_last, sa.Float) >= value)
        elif attr == 'link_dr_last_upto' and value is not None:
            query = query.filter(sa.func.cast(PageUrlDomainModel.link_dr_last, sa.Float) <= value)

        elif attr == 'link_price_avg_from' and value is not None:
            query = query.filter(sa.func.cast(PageUrlDomainModel.link_price_avg, sa.Float) >= value)
        elif attr == 'link_price_avg_upto' and value is not None:
            query = query.filter(sa.func.cast(PageUrlDomainModel.link_price_avg, sa.Float) <= value)

        elif attr == 'language_tags_id' and value is not None and value != []:
            language_tags_id = 0, *tuple(map(lambda x: int(x), value))
            query = query.filter(sa.text(f"""
            page_url_domain.id in (SELECT page_url_domain.id
                FROM page_url_domain 
                JOIN page_url_domain_tag AS pudomain_tag ON page_url_domain.id = pudomain_tag.page_url_domain_id 
                JOIN tag ON tag.id = pudomain_tag.tag_id
                WHERE tag.ref_property = 'language' AND tag.id IN {language_tags_id})"""))
        elif attr == 'country_tags_id' and value is not None and value != []:
            country_tags_id = 0, *tuple(map(lambda x: int(x), value))
            query = query.filter(sa.text(f"""
            page_url_domain.id in (SELECT page_url_domain.id
                FROM page_url_domain 
                JOIN page_url_domain_tag AS pudomain_tag ON page_url_domain.id = pudomain_tag.page_url_domain_id 
                JOIN tag ON tag.id = pudomain_tag.tag_id
                WHERE tag.ref_property = 'country' AND tag.id IN {country_tags_id})"""))

    return query


def paginate_query(Model: Base, query: Query, order_by: str, order: OrderEnum, pagination_params) -> Query:
    order = sa.desc if order.value == 'desc' else sa.asc
    query = query.order_by(order(getattr(Model, order_by))) \
        .offset(pagination_params["offset"]) \
        .limit(pagination_params["limit"])
    return query


def update_links(session: Session, links, linkchecks):
    for link in links:
        link_check = next((lc for lc in linkchecks if lc.link_id == link.id), None)
        link.link_check_last_id = link_check.id
        link.link_check_last_status = link_check.status
        link.link_check_last_result_message = link_check.result_message
    session.commit()


def get_next_proxy(
        proxy_ord_dict: OrderedDict | None = None,
        current_proxy: tuple | None = None,
) -> tuple | None:
    """return next proxy tuple ('AT Austria, Vienna', ('10.0.2.9', 3128)) or None if no more"""
    proxy_list = list(proxy_ord_dict.items())
    if current_proxy is None:
        return proxy_list[0]
    else:
        current_proxy_index = proxy_list.index(current_proxy)
        try:
            return proxy_list[current_proxy_index + 1]
        except IndexError:
            return None


def get_first_proxy(
        proxy_ord_dict: OrderedDict | None = None,
) -> tuple | None:
    """return first proxy tuple ('AT Austria, Vienna', ('10.0.2.9', 3128))"""
    if proxy_ord_dict is not None:
        first_c_name = next(iter(proxy_ord_dict))
        first_c_host_port = proxy_ord_dict[first_c_name]
        return first_c_name, first_c_host_port
    return None


def get_best_country_proxy(
        country_tag_name: str | None = None,
        proxy_ord_dict: OrderedDict | None = None,
) -> tuple | None:
    """return best proxy tuple according to  ('AUS Austria, Vienna', ('10.0.2.9', 3128)) or None if no more"""
    if country_tag_name is not None:
        for c_name, c_host_port in proxy_ord_dict.items():
            if country_tag_name in c_name:
                return c_name, c_host_port
    return get_first_proxy(proxy_ord_dict)


def get_proxies_dict(current_proxy: tuple | None = None) -> dict:
    # return proxies dict {'http://': 'http://10.0.2.3:3128', 'https://': 'https://10.0.2.3:3128'}

    if current_proxy is not None:
        return {
            'http://': f"http://{current_proxy[1][0]}:{current_proxy[1][1]}",
            'https://': f"https://{current_proxy[1][0]}:{current_proxy[1][1]}",
        }
    else:
        return {
            'http://': None,
            'https://': None,
        }


def get_proxy_for_playwright(proxies_dict):
    proxy = None
    if proxies_dict and proxies_dict.get('http://'):
        proxy = {
            'server': proxies_dict['http://'].replace('http://', '')
        }
    return proxy


def get_visit_from(current_proxy: tuple | None = None) -> str | None:
    # return str from current_proxy tuple or None if current_proxy is None
    return current_proxy[0] if current_proxy is not None else None


LIMITS_5 = httpx.Limits(max_connections=5)
TIMEOUT_2 = httpx.Timeout(connect=2, read=2, write=2, pool=None)
TIMEOUT_5 = httpx.Timeout(connect=5, read=5, write=5, pool=None)
TIMEOUT_30 = httpx.Timeout(connect=30, read=30, write=30, pool=None)
