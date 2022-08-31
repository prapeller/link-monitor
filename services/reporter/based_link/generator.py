import datetime

import openpyxl
import sqlalchemy as sa
from sqlalchemy.orm import Session

from core.exceptions import NotExcelException
from database.models.link import LinkModel
from database.models.user import UserModel


def generate_report(user: UserModel, db, template_filename, to_save_filepath):
    user_links = db.query(LinkModel).filter_by(user_id=user.id).all()

    try:
        wb = openpyxl.load_workbook(filename=template_filename)
    except KeyError:
        raise NotExcelException
    ws = wb.active

    for link in user_links:
        ws.append([
            link.page_url,
            link.anchor,
            link.link_url,
            link.da,
            link.dr,
            link.price,
            link.screenshot_url,
            link.contact,
            link.link_check_last.status,
            link.link_check_last.result_message,
            link.link_check_last.response_code
        ])
    wb.save(to_save_filepath)


def generate_filtered_links_report(links: list[LinkModel], template_filename, to_save_filepath):
    try:
        wb = openpyxl.load_workbook(filename=template_filename)
    except KeyError:
        raise NotExcelException
    ws = wb.active

    for link in links:
        ws.append([
            link.link_url_domain.name,
            link.page_url,
            link.link_url,
            link.anchor,
            link.da,
            link.dr,
            link.price,
            link.created_at,
        ])
    wb.save(to_save_filepath)


def count_linkchecklast_by_status(db, status, user_id, date_from, date_upto):
    row = db.execute(sa.text(f"""
    select count(l.link_id)
    from (select linkchecklasts.link_id, max(linkchecklasts.link_check_id) as linkcheck_last_id
          from (select link.id       as link_id,
                       link_check.id as link_check_id
                from link
                         join link_check on link.id = link_check.link_id
                         where link.created_at >= timestamp '{date_from} 00:00:01'
                         and link.created_at <= timestamp '{date_upto} 23:59:59'
                order by link_check_id, link_id) as linkchecklasts
          group by linkchecklasts.link_id
          order by linkchecklasts.link_id) l
             join link_check as lc on l.linkcheck_last_id = lc.id
             join link l2 on lc.link_id = l2.id
    where lc.status = '{status}' and l2.user_id = {user_id};
                """)).first()
    return row[0] if row else 0


def count_linkchecklast_by_status_v2(db, status, user_id, date_from, date_upto):
    row = db.execute(sa.text(f"""
    select count(link.link_check_last_status)
        from link
        where link.created_at >= timestamp '{date_from} 00:00:01'
          and link.created_at <= timestamp '{date_upto} 23:59:59'
          and link.link_check_last_status = '{status}'
          and link.user_id = {user_id};
          """)).first()
    return row[0] if row else 0


def count_status_growth(db, status, user_id, date_from, date_upto):
    row = db.execute(sa.text(f"""
    select count(distinct l_lcl2.l_id)
    from (select l_lcl.user_id,
                 l_lcl.link_id  as l_id,
                 l_lcl.lcl_id,
                 l_lcl.lcl_status,
                 lc3.id         as lc_id,
                 lc3.status     as lc_status,
                 lc3.created_at as lc_date
      from (select l2.user_id, l2.id as link_id, lcl.linkcheck_last_id as lcl_id, lc.status as lcl_status
            from (select linkchecks.link_id,
                         max(linkchecks.link_check_id) as linkcheck_last_id
                  from (select link.id       as link_id,
                               link_check.id as link_check_id
                        from link
                                 join link_check on link.id = link_check.link_id
                        order by link_id) as linkchecks
                  group by linkchecks.link_id
                  order by linkchecks.link_id) lcl
                     join link_check as lc on lcl.linkcheck_last_id = lc.id
                     join link l2 on lc.link_id = l2.id) as l_lcl
               join link_check lc3 on l_lcl.link_id = lc3.link_id
      where user_id = {user_id}
        and lcl_status = '{status}'
        and l_lcl.lcl_status != lc3.status
        and lc3.created_at >= timestamp '{date_from} 00:00:01'
        and lc3.created_at <= timestamp '{date_upto} 23:59:59') as l_lcl2;
                """)).first()
    return row[0] if row else 0


def count_status_growth_v2(db, status, user_id, date_from, date_upto):
    row = db.execute(sa.text(f"""
    select count(distinct link_link_checks.link_id)
                  from (select link.id       as link_id
                        from link
                                 join link_check on link.id = link_check.link_id
                        where link_check.created_at >= timestamp '{date_from} 00:00:01'
                        and link_check.created_at <= timestamp '{date_upto} 23:59:59'
                        and link.link_check_last_status != link_check.status
                        and link.link_check_last_status = '{status}'
                        and link.user_id = {user_id}
                        ) as link_link_checks;
                """)).first()
    return row[0] if row else 0


def get_dashboard_data(db: Session, users: list[UserModel], date_from: datetime.date, date_upto: datetime.date):
    dashboard_data = []
    for user in users:
        user: UserModel
        start_time = datetime.datetime.now()
        user_links_select_query = sa.select(LinkModel).filter(LinkModel.user_id == user.id)
        finish_time = datetime.datetime.now()
        # print(f'user {user}, user_links time: {finish_time - start_time}')

        mean_da = 0
        mean_dr = 0
        mean_price = 0
        total_links_count = 0
        green_links_count = 0
        red_links_count = 0
        period_link_growth_green = 0
        period_link_growth_red = 0

        if db.execute(user_links_select_query).first() is not None:
            user_links_within_dates_select_query = user_links_select_query \
                .filter(sa.text(f"link.created_at >= timestamp '{date_from} 00:00:01'"
                                f"and link.created_at <= timestamp '{date_upto} 23:59:59'"))

            start_time = datetime.datetime.now()
            if db.execute(user_links_within_dates_select_query).first() is not None:
                mean_da_query_result = db.execute(
                    sa.select(sa.func.avg(sa.text('anon_1.da'))) \
                        .select_from(user_links_within_dates_select_query)
                ).first()[0]
                if mean_da_query_result is not None:
                    mean_da = float(mean_da_query_result)
                mean_dr_query_result = db.execute(
                    sa.select(sa.func.avg(sa.text('anon_1.dr'))) \
                        .select_from(user_links_within_dates_select_query)
                ).first()[0]
                if mean_dr_query_result is not None:
                    mean_dr = float(mean_dr_query_result)
                mean_price_query_result = db.execute(
                    sa.select(sa.func.avg(sa.text('anon_1.price'))) \
                        .select_from(user_links_within_dates_select_query)
                ).first()[0]
                if mean_price_query_result is not None:
                    mean_price = float(mean_price_query_result)
                finish_time = datetime.datetime.now()
                # print(f'user {user}, mean time: {finish_time - start_time}')

                start_time = datetime.datetime.now()
                total_links_count_query_result = db.execute(
                    sa.select(sa.func.count(sa.text('anon_1.id'))) \
                        .select_from(user_links_within_dates_select_query)
                ).first()[0]
                if total_links_count_query_result is not None:
                    total_links_count = total_links_count_query_result
                green_links_count = count_linkchecklast_by_status_v2(db, 'green', user.id, date_from, date_upto)
                red_links_count = count_linkchecklast_by_status_v2(db, 'red', user.id, date_from, date_upto)
                finish_time = datetime.datetime.now()
                # print(f'user {user}, count time: {finish_time - start_time}')

                start_time = datetime.datetime.now()
                period_link_growth_green = count_status_growth_v2(db, 'green', user.id, date_from, date_upto)
                period_link_growth_red = count_status_growth_v2(db, 'red', user.id, date_from, date_upto)
                finish_time = datetime.datetime.now()
                # print(f'user {user}, growth time: {finish_time - start_time}')

        user_data = {
            'user': f'{user.first_name} {user.last_name}',
            'mean_da': f'{mean_da:.2f}',
            'mean_dr': f'{mean_dr:.2f}',
            'mean_price': f'{mean_price:.2f}',
            'total_links_count': total_links_count,
            'green_links_count': green_links_count,
            'red_links_count': red_links_count,
            'period_link_growth_green': period_link_growth_green,
            'period_link_growth_red': period_link_growth_red,
        }
        dashboard_data.append(user_data)
    return dashboard_data
