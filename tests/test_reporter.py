import datetime

from services.reporter.based_link_url_domain.generator import get_week_number, get_year_week

date_2021_01_29 = datetime.datetime(2021, 1, 29)


def test_get_year_week_1():
    year_week_for_2021_01_29 = get_year_week(date=date_2021_01_29)
    assert year_week_for_2021_01_29 == 5


def test_get_week_number_1():
    week_n_for_2021_01_29 = get_week_number(date=date_2021_01_29)
    assert week_n_for_2021_01_29 == 5
