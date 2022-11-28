import asyncio
import ssl
import subprocess
from datetime import datetime

import httpx
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from core.config import settings
from core.exceptions import CheckWithPlaywrightException
from core.shared import (
    chunks_generator,
    normalize,
    remove_https,
    update_links,
    get_proxy_for_playwright,
    get_next_proxy,
    get_proxies_dict,
    get_visit_from, LIMITS_5, TIMEOUT_2, TIMEOUT_5
)
from database.crud import create_many
from database.models.link import LinkModel
from database.models.link_check import LinkCheckModel
from database.schemas.link_check import LinkCheckCreateSerializer
from services.domain_checker import (
    get_domain_name_from_url,
    recreate_domains,
    check_pudomains_with_similarweb
)


def get_status_and_message(
        response_code: int,
        redirect_codes_list: list[int],
        href_has_link_url_domain: bool,
        href_with_link_url_domain: str,
        href_is_found: bool,
        rel_has_nofollow: bool,
        rel_has_sponsored: bool,
        meta_robots_has_noindex: bool,
        meta_robots_has_nofollow: bool,
        anchor_text: str,
        anchor_text_found: str,
        mode: str | None,
        visit_from: str | None
):
    status = ''
    message = ''

    if 200 not in redirect_codes_list:
        status = 'red'
        message += f'code: {response_code};\n'
        return status, message

    if not href_is_found:
        status = 'red'
        if href_has_link_url_domain:
            message += f'found href "{href_with_link_url_domain}" differs;\n'
        else:
            message += 'acceptor not found;\n'
    if rel_has_nofollow:
        status = 'red'
        message += 'rel has nofollow;\n'
    if rel_has_sponsored:
        status = 'red'
        message += 'rel has sponsored;\n'
    if meta_robots_has_noindex:
        status = 'red'
        message += 'robots has noindex;\n'
    if meta_robots_has_nofollow:
        status = 'red'
        message += 'robots has nofollow;\n'
    if anchor_text_found != '' and (normalize(anchor_text_found) != normalize(anchor_text)):
        status = 'red'
        message += f'found anchor text "{anchor_text_found}" differs;\n'
    if not status:
        status = 'green'
        message = 'ok;\n'
    if mode:
        message += f'mode: {mode};\n'
    if visit_from:
        message += f'visit_from: {visit_from};\n'

    return status, message


class LinkChecker:

    def __init__(self, session, start_mode=None):

        self.session = session
        self.start_mode = start_mode
        self.lcs_list = []
        self.check_with_proxies_link_ids = []
        self.check_with_pw_link_ids = []

    def __repr__(self):
        return f"""<LinkChecker> (id: {id(self)}
        lcs_list: {self.lcs_list}
        check_with_proxies_link_ids: {self.check_with_proxies_link_ids}
        check_with_pw_link_ids: {self.check_with_pw_link_ids})"""

    async def check_links(
            self, links: list[LinkModel],
            timeout=TIMEOUT_5, limits=LIMITS_5,
            mode: str | None = None,
            proxies_dict: dict | None = None,
            visit_from: str | None = None,
    ):
        if self.start_mode is None:
            # first fill link_check_serializer_list (lcs_list),
            self.lcs_list = await self.get_linkcheck_ser_list(
                links,
                timeout=timeout, limits=limits,
                mode=mode, proxies_dict=proxies_dict, visit_from=visit_from,
            )

        if self.start_mode == 'playwright':
            self.check_with_pw_link_ids = [link.id for link in links]

        # if check_with_proxies_lisk_ids, recheck them with proxies
        if self.check_with_proxies_link_ids:
            await self.check_links_with_proxies()

        # if check_with_playwright_link_ids, recheck them with playwright
        if self.check_with_pw_link_ids:
            await self.check_links_with_playwright()

        # then create linkchecks based on this lcs_list
        linkchecks = create_many(self.session, LinkCheckModel, serializers=self.lcs_list)

        # then update link.link_check_last_id, link.link_check_last_status, link.link_check_last_result_message
        update_links(self.session, links, linkchecks)

        # then start SSL checking of created links
        linkchecks_id_list = [str(linkcheck.id) for linkcheck in linkchecks]
        subprocess.run(
            ["python3.10", "ssl_cli.py", "-l", *linkchecks_id_list],
        )

    async def check_links_with_proxies(self):
        # current_proxy = ('AT Austria, Vienna', ('10.0.2.9', 3128))
        current_proxy = get_next_proxy(proxy_ord_dict=settings.LINK_CHECKER_PROXY_ORDERED_DICT)
        while self.check_with_proxies_link_ids and current_proxy is not None:
            current_proxies_dict = get_proxies_dict(current_proxy)
            current_visit_from = get_visit_from(current_proxy)

            self.remove_errored_from_lcs_list(self.check_with_proxies_link_ids)

            links = self.session.query(LinkModel).filter(LinkModel.id.in_(self.check_with_proxies_link_ids)).all()
            self.check_with_proxies_link_ids = []
            lcs_list_new = await self.get_linkcheck_ser_list(
                links,
                timeout=TIMEOUT_2, limits=LIMITS_5,
                mode=None, proxies_dict=current_proxies_dict, visit_from=current_visit_from
            )
            self.lcs_list.extend(lcs_list_new)
            current_proxy = get_next_proxy(proxy_ord_dict=settings.LINK_CHECKER_PROXY_ORDERED_DICT,
                                           current_proxy=current_proxy)
            # if still timeout_link_ids, then check with another proxy
        # if still timeout_link_ids after all proxies, then check with playwright
        if self.check_with_proxies_link_ids:
            self.check_with_pw_link_ids.extend(self.check_with_proxies_link_ids)
            self.check_with_proxies_link_ids = []

    async def check_links_with_playwright(self):
        self.remove_errored_from_lcs_list(self.check_with_pw_link_ids)

        current_proxy = get_next_proxy(proxy_ord_dict=settings.LINK_CHECKER_PROXY_ORDERED_DICT)
        current_proxies_dict = get_proxies_dict(current_proxy)
        current_visit_from = get_visit_from(current_proxy)

        check_with_pw_links = self.session.query(LinkModel).filter(LinkModel.id.in_(self.check_with_pw_link_ids)).all()
        self.check_with_pw_link_ids = []
        for link_chunk in chunks_generator(check_with_pw_links, chunk_size=settings.PLAYWRIGHT_LINK_CHUNK_SIZE):
            lcs_list_new = await self.get_linkcheck_ser_list(
                link_chunk,
                mode='playwright', proxies_dict=current_proxies_dict, visit_from=current_visit_from
            )
            print(f'time: {datetime.now()}\n'
                  f'PLAYWRIGHT_LINK_CHUNK_SIZE: {settings.PLAYWRIGHT_LINK_CHUNK_SIZE}...\n\n\n')
            self.lcs_list.extend(lcs_list_new)

    async def get_linkcheck_ser_list(self,
                                     links: list[LinkModel],
                                     timeout=TIMEOUT_5, limits=LIMITS_5,
                                     mode=None, proxies_dict=None, visit_from=None
                                     ) -> list:
        async with httpx.AsyncClient(timeout=timeout, limits=limits, proxies=proxies_dict) as client:
            for link in links:
                pudomain_created, ludomain_created = recreate_domains(self.session, link)
                if pudomain_created:
                    check_pudomains_with_similarweb.delay(id_list=[link.page_url_domain_id])

                tasks = [
                    self.get_link_check_ser(client, link, mode=mode, proxies_dict=proxies_dict, visit_from=visit_from)
                    for link in links]
            link_check_ser_list = list(await asyncio.gather(*tasks))
            return link_check_ser_list

    async def get_link_check_ser(self, client: httpx.AsyncClient, link: LinkModel,
                                 mode=None, proxies_dict=None, visit_from=None):
        start_time = datetime.now()
        print(f'started getting soup data, mode: {mode}, from: {visit_from}, '
              f'link.id: {link.id}, link.page_url {link.page_url}')

        response_code = None
        redirect_codes_list = []
        redirect_url = ''

        anchor_text_found = ''
        anchor_count = 0
        link_url_others_count = 0
        href_has_link_url_domain = False
        href_with_link_url_domain = ''
        href_is_found = False
        href_has_rel = False
        rel_has_nofollow = False
        rel_has_sponsored = False
        meta_robots_has_noindex = False
        meta_robots_has_nofollow = False
        response_text = ''

        link_url_without_https = remove_https(link.link_url)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

        async def set_response_code(response_status):
            nonlocal response_code
            response_code = response_status

        async def append_redirect_codes_list(response_status):
            nonlocal redirect_codes_list
            if response_status == 200 and redirect_codes_list.count(200) > 0:
                pass
            else:
                redirect_codes_list.append(response_status)

        try:
            # get response_code and response_text with playwright
            if mode == 'playwright':
                async with async_playwright() as p:
                    browser = await p.webkit.launch(
                        proxy=get_proxy_for_playwright(proxies_dict),
                        headless=True
                    )
                    page = await browser.new_page(ignore_https_errors=True)
                    page.on("response", lambda response: set_response_code(response.status))
                    page.on("response", lambda response: append_redirect_codes_list(response.status))
                    print('playwright working...')
                    await page.goto(link.page_url)
                    await page.wait_for_timeout(15000)
                    response_text = await page.content()
                    await browser.close()

            # get response_code and response_text with httpx.AsyncClient
            else:
                request = client.build_request("GET", link.page_url, headers=headers)
                while request is not None:
                    response = await client.send(request)
                    start_time = datetime.now()
                    response_code = response.status_code
                    redirect_codes_list.append(response_code)
                    if len(redirect_codes_list) > 20:
                        break
                    if response.next_request:
                        redirect_url = str(response.next_request.url)
                    try:
                        response_text = response.content.decode('utf-8', 'strict')
                    except UnicodeDecodeError:
                        try:
                            response_text = response.content.decode('latin-1', 'strict')
                        except UnicodeDecodeError:
                            response_text = response.content.decode('utf-8', 'ignore')

                    request = response.next_request
                if response_code == 403 or response_code == 503:
                    raise CheckWithPlaywrightException(f'forbidden with response code {response_code}',
                                                       response_code=response_code)

            # getting soup data
            soup = BeautifulSoup(response_text, 'html.parser')
            for m in soup.find_all('meta'):
                m_name = m.get('name')
                if m_name == 'robots':
                    m_content = m.get('content')
                    if 'noindex' in m_content:
                        meta_robots_has_noindex = True
                    if 'nofollow' in m_content:
                        meta_robots_has_nofollow = True
                    break
            found_anchors = soup.find_all('a')

            # count anchor.link_url == link.link_url from all found_anchors
            for a in found_anchors:
                current_a_href = a.get('href')
                if current_a_href is None:
                    continue
                if current_a_href == link.link_url \
                        or current_a_href.strip('/') == link.link_url.strip('/') \
                        or current_a_href.strip('/') == link_url_without_https.strip('/'):
                    anchor_count += 1

            # check matches with link
            for a in found_anchors:

                current_a_href = a.get('href')
                if current_a_href is None:
                    continue
                current_a_href_domain_name = get_domain_name_from_url(current_a_href) if current_a_href else None
                if current_a_href_domain_name:
                    # check if current_a_href goes to other domain
                    if current_a_href_domain_name not in (link.page_url_domain.name,
                                                          link.link_url_domain.name):
                        link_url_others_count += 1
                        continue
                    # check if current_a_href goes to acceptor domain
                    if current_a_href_domain_name == link.link_url_domain.name:
                        href_has_link_url_domain = True
                        href_with_link_url_domain = current_a_href
                        # check if current_a_href is the same as link_url
                        if current_a_href == link.link_url \
                                or current_a_href.strip('/') == link.link_url.strip('/') \
                                or current_a_href.strip('/') == link_url_without_https.strip('/'):
                            href_is_found = True
                            anchor_text_found = a.getText()

                            rel = a.get('rel')
                            if rel:
                                href_has_rel = True
                                if 'nofollow' in rel:
                                    rel_has_nofollow = True
                                if 'sponsored' in rel:
                                    rel_has_sponsored = True
                            # if at least once href_is_found, no need to seek further
                            break

            # issue #70: for cases that require loading js scripts first and then parsing data
            # issue #75: there are sites that render hrefs depending on current location, so better check with playwright and proxy
            if (
                    mode is None and
                    visit_from is None and
                    response_code == 200 and
                    not href_has_link_url_domain and
                    not href_is_found
            ):
                raise CheckWithPlaywrightException(
                    f'response code: 200, but havn\'t found project domain or acceptor, trying to load js script first...',
                    response_code=response_code)

            status, result_message = get_status_and_message(
                response_code=response_code,
                redirect_codes_list=redirect_codes_list,
                href_has_link_url_domain=href_has_link_url_domain,
                href_with_link_url_domain=href_with_link_url_domain,
                href_is_found=href_is_found,
                rel_has_nofollow=rel_has_nofollow,
                rel_has_sponsored=rel_has_sponsored,
                meta_robots_has_noindex=meta_robots_has_noindex,
                meta_robots_has_nofollow=meta_robots_has_nofollow,
                anchor_text=link.anchor,
                anchor_text_found=anchor_text_found,
                mode=mode,
                visit_from=visit_from)

        except httpx.TimeoutException as e:
            status = 'red'
            result_message = f"error: {str(e.__class__).replace('<', '').replace('>', '')} waited({client.timeout.read} sec) {str(e)}\nmode: {mode}\nvisit_from: {visit_from}\n"
            self.check_with_proxies_link_ids.append(link.id)
            print(result_message)
        except (ssl.SSLError, ssl.SSLCertVerificationError) as e:
            status = 'red'
            result_message = f"error: {str(e.__class__).replace('<', '').replace('>', '')} {str(e)}\nmode: {mode}\nvisit_from: {visit_from}\n"
            self.check_with_pw_link_ids.append(link.id)
            print(result_message)
        except CheckWithPlaywrightException as e:
            status = 'red'
            result_message = f"error: {str(e.__class__).replace('<', '').replace('>', '')} {str(e)}\nmode: {mode}\nvisit_from: {visit_from}\n"
            self.check_with_pw_link_ids.append(link.id)
            print(result_message)
        except Exception as e:
            status = 'red'
            result_message = f"error: {str(e.__class__).replace('<', '').replace('>', '')} {str(e)}\nmode: {mode}\nvisit_from: {visit_from}\n"
            print(result_message)

        link_check_ser = LinkCheckCreateSerializer(
            link_id=link.id,
            # response_text=response_text if mode == 'playwright' else None,
            response_code=response_code,
            redirect_codes_list=str(redirect_codes_list),
            redirect_url=redirect_url,
            anchor_text_found=anchor_text_found,
            anchor_count=anchor_count,
            link_url_others_count=link_url_others_count,
            href_is_found=href_is_found,
            href_has_rel=href_has_rel,
            rel_has_nofollow=rel_has_nofollow,
            rel_has_sponsored=rel_has_sponsored,
            meta_robots_has_noindex=meta_robots_has_noindex,
            meta_robots_has_nofollow=meta_robots_has_nofollow,
            status=status,
            result_message=result_message
        )

        finish_time = datetime.now()
        print(
            f'finished getting soup data, link.id: {link.id}, executing time: {finish_time - start_time}')
        return link_check_ser

    def remove_errored_from_lcs_list(self, error_link_ids):
        error_lcs_list = [lcs for lcs in self.lcs_list if lcs.link_id in error_link_ids]

        for error_lcs in error_lcs_list:
            self.lcs_list.remove(error_lcs)
