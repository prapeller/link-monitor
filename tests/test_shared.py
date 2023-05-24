from core.shared import get_year_month_period

year_month_period_from_october_2022_upto_feb_2023 = [
    (2022, 10),
    (2022, 11),
    (2022, 12),
    (2023, 1),
    (2023, 2)
]

year_month_period_from_november_2022_upto_jan_2024 = [
    (2022, 11),
    (2022, 12),
    (2023, 1),
    (2023, 2),
    (2023, 3),
    (2023, 4),
    (2023, 5),
    (2023, 6),
    (2023, 7),
    (2023, 8),
    (2023, 9),
    (2023, 10),
    (2023, 11),
    (2023, 12),
    (2024, 1),
]


def test_get_year_month_period():
    year_month_period = get_year_month_period({'year_from': 2022, 'month_from': 10,
                                               'year_upto': 2023, 'month_upto': 2})
    assert year_month_period == year_month_period_from_october_2022_upto_feb_2023

    year_month_period = get_year_month_period({'year_from': 2022, 'month_from': 11,
                                               'year_upto': 2024, 'month_upto': 1})
    assert year_month_period == year_month_period_from_november_2022_upto_jan_2024
