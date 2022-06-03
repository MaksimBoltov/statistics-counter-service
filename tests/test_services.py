import datetime

import pytest
from sqlalchemy.orm import Session

from app import models, schemas
from app.services import _get_cpc, _get_cpm, get_returns_statistics

STATISTICS_LIST_LEN = 3
VIEWS_COUNT = 100
CLICKS_COUNT = 150
COSTS_VALUE = 30.0


@pytest.fixture()
def get_statistics_list() -> list[models.Statistics]:
    """Returns a list of models.Statistics objects for tests."""
    date = [f"2000-01-0{_}" for _ in range(1, STATISTICS_LIST_LEN + 1)]
    views = [VIEWS_COUNT * _ for _ in range(1, STATISTICS_LIST_LEN + 1)]
    clicks = [CLICKS_COUNT * _ for _ in range(1, STATISTICS_LIST_LEN + 1)]
    costs = [COSTS_VALUE * _ for _ in range(1, STATISTICS_LIST_LEN + 1)]
    statistics = []
    for d, v, cl, co in zip(date, views, clicks, costs):
        st = schemas.Statistics(date=d, views=v, clicks=cl, cost=co)
        statistics.append(models.Statistics(**st.dict()))
    return statistics


@pytest.mark.parametrize(
    "cost, clicks",
    [(0, 100), (1, 1), (2000, 1), (200, 100)],
)
def test_cpc(cost: float, clicks: int) -> None:
    """Testing counting of the average cost per click."""
    result = round(cost / clicks, 2)
    assert result == _get_cpc(cost, clicks)


@pytest.mark.parametrize(
    "cost, clicks",
    [(0, 0), (100, 0)],
)
def test_cpc_zero_division(cost: float, clicks: int) -> None:
    """Testing counting of the average cost per click when count of clicks equal 0."""
    assert _get_cpc(cost, clicks) is None


@pytest.mark.parametrize(
    "cost, views",
    [(0, 1000), (1, 1), (2000, 1), (200, 100)],
)
def test_cpm(cost: float, views: int) -> None:
    """Testing counting of the average cost per 1000 views."""
    result = round(cost / views * 1000, 2)
    assert result == _get_cpm(cost, views)


@pytest.mark.parametrize(
    "cost, views",
    [(0, 0), (100, 0)],
)
def test_cpm_zero_division(cost: float, views: int) -> None:
    """Testing counting of the average cost per 1000 views when count of views
    equal 0.
    """
    assert _get_cpm(cost, views) is None


def test_returns_statistics_without_filter(db: Session) -> None:
    """Testing refactoring list of models.Statistics for output."""
    date = [f"2000-01-0{_}" for _ in range(1, 4)]
    views = [100 * _ for _ in range(1, 4)]
    clicks = [150 * _ for _ in range(1, 4)]
    cost = [30 * _ for _ in range(1, 4)]
    statistics = []
    for d, v, cl, co in zip(date, views, clicks, cost):
        st = schemas.Statistics(date=d, views=v, clicks=cl, cost=co)
        statistics.append(models.Statistics(**st.dict()))

    return_statistics = get_returns_statistics(statistics)
    first_date = datetime.date(*[int(_) for _ in date[0].split("-")])

    assert len(return_statistics) == 3
    assert first_date in return_statistics
    assert return_statistics[first_date]["date"] == first_date
    assert return_statistics[first_date]["views"] == views[0]
    assert return_statistics[first_date]["clicks"] == clicks[0]
    assert return_statistics[first_date]["cost"] == cost[0]
    assert return_statistics[first_date]["cpc"] == round(cost[0] / clicks[0], 2)
    assert return_statistics[first_date]["cpm"] == round(cost[0] / views[0] * 1000, 2)


def test_returns_statistics_filter_cost(get_statistics_list) -> None:
    """Testing filter of 'cost' field of model Statistics (without reversed)."""
    statistics = get_statistics_list
    return_statistics = get_returns_statistics(statistics, "cost", False)
    firs_key = list(return_statistics.keys())[0]
    assert firs_key == datetime.date(2000, 1, 1)
    assert return_statistics[firs_key]["cost"] == COSTS_VALUE


def test_returns_statistics_filter_cost_reversed(get_statistics_list) -> None:
    """Testing filter of 'cost' field of model Statistics with reversing."""
    statistics = get_statistics_list
    return_statistics = get_returns_statistics(statistics, "cost", True)
    firs_key = list(return_statistics.keys())[0]
    assert firs_key == datetime.date(2000, 1, 1 * STATISTICS_LIST_LEN)
    assert return_statistics[firs_key]["cost"] == COSTS_VALUE * STATISTICS_LIST_LEN


def test_returns_statistics_reversed_without_filter(get_statistics_list) -> None:
    """Testing filter model Statistics without a specific field but with reversing."""
    statistics = get_statistics_list
    return_statistics = get_returns_statistics(statistics, None, True)
    firs_key = list(return_statistics.keys())[0]
    assert firs_key == datetime.date(2000, 1, 1 * STATISTICS_LIST_LEN)
    assert return_statistics[firs_key]["cost"] == COSTS_VALUE * STATISTICS_LIST_LEN
