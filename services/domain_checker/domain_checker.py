import logging
import multiprocessing
import re
from copy import copy

from bs4 import BeautifulSoup
from bs4.element import Comment
from langdetect import detect as detect_language
from playwright._impl._api_types import TimeoutError as PlaywrightTimeError
from playwright.async_api import async_playwright
from sqlalchemy.orm import Session

from core.config import settings
from core.countries import COUNTRIES_DICT
from core.languages import LANGUAGES_DICT
from core.shared import (
    get_proxy_for_playwright,
    get_next_proxy,
    get_proxies_dict,
    get_best_country_proxy,
)
from database import SessionLocal
from database.crud import get_or_create_by_name
from database.models.link import LinkModel
from database.models.link_url_domain import LinkUrlDomainModel
from database.models.page_url_domain import PageUrlDomainModel
from database.models.tag import TagModel
from database.repository import SqlAlchemyRepository
from database.schemas.tag import TagCreateSerializer


logger = logging.getLogger(name='domain_checker')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s ")
file_handler = logging.FileHandler(f'services/domain_checker/domain_checker.log', encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def get_domain_name_from_url(page_url) -> str | None:
    match = re.search(
        pattern=r"(?:https?:)?(?:\/\/)?(?:[^@\/\n]+@)?(?:www\.)?([^:\/?\n]+\.[^:\/?\n]+)",
        string=page_url.lower()
    )
    domain_name = match.group(1) if match else ''
    return domain_name


def recreate_pudomain(session, link: LinkModel) -> bool:
    pudomain_name = get_domain_name_from_url(link.page_url)
    pudomain, created = get_or_create_by_name(session, PageUrlDomainModel, name=pudomain_name)
    pudomain.update_pudomain_link_last(link_last=link)
    pudomain.update_link_price_avg()
    link.page_url_domain = pudomain
    return created


def recreate_ludomain(session, link: LinkModel) -> bool:
    ludomain_name = get_domain_name_from_url(link.link_url)
    ludomain, created = get_or_create_by_name(session, LinkUrlDomainModel, name=ludomain_name)
    link.link_url_domain = ludomain
    return created


def recreate_domains(session: Session, link: LinkModel) -> tuple[bool, bool]:
    pudomain_created = recreate_pudomain(session, link)
    ludomain_created = recreate_ludomain(session, link)
    session.commit()
    session.refresh(link)
    return pudomain_created, ludomain_created


def clean_countries_list(countries_list: list) -> list:
    countries_list = countries_list.copy()
    if countries_list:
        if '' in countries_list:
            countries_list.remove('')
        if 'Other countries' in countries_list:
            countries_list.remove('Other countries')
    return countries_list


def get_pud_country_tag_name(pud):
    pud_country_tags = [tag for tag in pud.tags if tag.ref_property == 'country']
    first_pud_country_tag = None
    if pud_country_tags:
        first_pud_country_tag = pud_country_tags[0]
    pud_country_tag_name = None
    if first_pud_country_tag is not None:
        pud_country_tag_name = first_pud_country_tag.name
    return pud_country_tag_name


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def get_visible_text_from_page_content(page_content):
    soup = BeautifulSoup(page_content, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)


async def create_from_similar_web_for_pud(pud_id, to_create=('country_tags', 'month_visits')):
    """open playwright browser with similarweb.com check page
    - check last month countries and create country tags for page_url_domain
    - check last month traffic and mark it for page_url_domain
    """
    session = SessionLocal()
    repo = SqlAlchemyRepository(session)
    pud: PageUrlDomainModel = repo.get(PageUrlDomainModel, id=pud_id)
    assert pud is not None, f'domain with id: {pud_id} wasnt found'

    proxy = get_next_proxy(proxy_ord_dict=settings.DOMAIN_CHECKER_PROXY_ORDERED_DICT,
                           current_proxy=None)
    proxies_dict = get_proxies_dict(proxy)

    async with async_playwright() as p:
        browser = await p.firefox.launch(
            proxy=get_proxy_for_playwright(proxies_dict=proxies_dict),
            headless=True,
        )
        page = await browser.new_page()
        url = f'https://www.similarweb.com/website/{pud.name}'
        await page.goto(url)
        logger.debug(f'\n<<<>>> Opened browser: {browser}, url {url}, visit_from {proxy}')

        if 'country_tags' in to_create:
            found_countries_str = await page.text_content(selector='.wa-geography__chart-legend')

            countries_list = re.split(r'[^a-zA-Z\s]+', found_countries_str)
            countries_list = clean_countries_list(countries_list)
            pud_country_tags = []

            for country in countries_list:
                for full_name, name in COUNTRIES_DICT.items():
                    if country in full_name:
                        country_tag_ser = TagCreateSerializer(name=name, full_name=full_name, ref_property='country')
                        country_tag = repo.get_or_create(TagModel, country_tag_ser)
                        pud_country_tags.append(country_tag)
                        break

            if pud_country_tags:
                pud_country_tags = list(set(pud_country_tags))
                pud.country_tags = pud_country_tags
                session.commit()
                logger.debug(f'===>>> Set for domain: {pud} COUNTRY TAGS: {pud_country_tags}')

        if 'month_visits' in to_create:
            total_visits = await page.text_content(selector='.engagement-list__item-value')
            pud.last_month_visits = total_visits
            session.commit()
            logger.debug(f'===>>> Set for domain: {pud} MONTHS VISITS: {total_visits}')

        await browser.close()
        session.close()


async def get_page_content_with_playwright(pud: PageUrlDomainModel,
                                           timeout=2000,
                                           proxy=None,
                                           ) -> str:
    url = f'https://{pud.name}'
    proxies_dict = get_proxies_dict(proxy)

    async with async_playwright() as p:
        browser = await p.webkit.launch(
            proxy=get_proxy_for_playwright(proxies_dict=proxies_dict),
            headless=True,
            timeout=timeout
        )
        page = await browser.new_page(ignore_https_errors=True)
        await page.goto(url)
        page_content = await page.content()
        logger.debug(f'\n<<<>>> Opened browser: {browser}, url {url}, visit_from {proxy}')
        await browser.close()
        return page_content


async def get_pud_main_page_content(pud, start_proxy):
    proxy = copy(start_proxy)
    page_content = ''
    while page_content == '' and proxy is not None:
        try:
            page_content = await get_page_content_with_playwright(pud=pud, proxy=proxy)
        except PlaywrightTimeError:
            proxy = get_next_proxy(proxy_ord_dict=settings.DOMAIN_CHECKER_PROXY_ORDERED_DICT,
                                   current_proxy=proxy)
    return page_content


async def create_language_tags_for_pud(pud_id):
    session = SessionLocal()
    repo = SqlAlchemyRepository(session)
    pud: PageUrlDomainModel = repo.get(PageUrlDomainModel, id=pud_id)
    assert pud is not None, f'domain with id: {pud_id} wasnt found'
    pud_country_tag_name = get_pud_country_tag_name(pud)

    proxy = get_best_country_proxy(
        country_tag_name=pud_country_tag_name,
        proxy_ord_dict=settings.DOMAIN_CHECKER_PROXY_ORDERED_DICT,
    )
    page_content = await get_pud_main_page_content(pud, proxy)
    main_page_text = get_visible_text_from_page_content(page_content)
    language_2 = detect_language(main_page_text)

    for language_full, langs in LANGUAGES_DICT.items():
        if language_2 in langs:
            language_3 = langs[0]
            language_tag_ser = TagCreateSerializer(name=language_3, full_name=language_full,
                                                   ref_property='language')
            language_tag = repo.get_or_create(TagModel, language_tag_ser)

            pud.language_tags = language_tag
            session.commit()
            logger.debug(f'===>>> Set for domain: {pud} LANGUAGE TAG: {language_tag}')
            session.close()
            break


class PageUrlDomainChecker:
    """pud - page_url_domain
    pud_id_queue - queue made of page_url_domain ids for checking,
    pud_id can be added to queue for checking from different celery tasks (different processes)
    so pud_id_queue should be shared list
    """

    queue_lock = multiprocessing.Lock()
    __pud_id_queue = multiprocessing.Manager().list()
    __is_checking = multiprocessing.Manager().list([False])

    def __init__(self, pudomain_id_list: list[int] = None):
        with self.queue_lock:
            for pud_id in pudomain_id_list:
                if pud_id not in self.__pud_id_queue:
                    self.__pud_id_queue.append(pud_id)
            logger.info(f"__init__ {self}")

    def __repr__(self):
        return f"""<PageUrlDomainChecker>, id: {id(self)}, pud_id_queue:{self.__pud_id_queue}"""

    def get_first_from_pud_id_queue(self):
        with self.queue_lock:
            pud_id = None
            if len(self.__pud_id_queue) > 0:
                pud_id = self.__pud_id_queue[0]
                self.__pud_id_queue.remove(pud_id)
            return pud_id

    async def run_check(self):
        with self.queue_lock:
            if self.__is_checking[0]:
                print(f'stop check, another one already checking')
                return
            else:
                self.__is_checking[0] = True

        while True:
            pud_id = self.get_first_from_pud_id_queue()

            if pud_id is not None:
                try:
                    await create_from_similar_web_for_pud(pud_id, to_create=('country_tags', 'month_visits'))
                except Exception as e:
                    print(f'ERROR while Creating from similarweb.com for pud_id {pud_id}', e)
                try:
                    await create_language_tags_for_pud(pud_id)
                except Exception as e:
                    print(f'ERROR while Creating language tags for pud_id {pud_id}', e)

            else:
                self.__is_checking[0] = False
                break
