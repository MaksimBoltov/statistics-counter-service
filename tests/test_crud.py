import datetime

import pytest
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app import models, schemas
from app.crud import (
    create_statistics, delete_all_statistics,
    get_statistics_for_date, get_statistics_for_date_period,
    summarize_or_create_statistics, summarize_statistics
)
from app.exceptions import UniqueViolationException

STATISTICS_LIST_LEN = 3
VIEWS_COUNT = 100
CLICKS_COUNT = 150
COSTS_VALUE = 30.0


@pytest.fixture()
def db_with_data(db: Session) -> Session:
    """Returns db with data for tests."""
    date = [f"2000-01-0{_}" for _ in range(1, STATISTICS_LIST_LEN + 1)]
    views = [VIEWS_COUNT * _ for _ in range(1, STATISTICS_LIST_LEN + 1)]
    clicks = [CLICKS_COUNT * _ for _ in range(1, STATISTICS_LIST_LEN + 1)]
    costs = [COSTS_VALUE * _ for _ in range(1, STATISTICS_LIST_LEN + 1)]
    for d, v, cl, co in zip(date, views, clicks, costs):
        st = schemas.Statistics(date=d, views=v, clicks=cl, cost=co)
        db.add(models.Statistics(**st.dict()))
    db.commit()
    return db


@pytest.mark.parametrize(
    "date, views, clicks, cost",
    [(datetime.date(2000, 1, 1), 100, 200, 300)],
)
def test_create_new_statistics(
    db: Session, date: datetime.date, views: int, clicks: int, cost: float
) -> None:
    """Tests the creation statistics in the database."""
    statistics_in = schemas.Statistics(
        date=date, views=views, clicks=clicks, cost=cost
    )
    statistics = create_statistics(db, statistics=statistics_in)
    assert statistics
    assert jsonable_encoder(statistics) == jsonable_encoder(statistics_in)
    assert db.query(models.Statistics).count() == 1
    assert db.query(models.Statistics).first() == statistics


@pytest.mark.parametrize(
    "date, views, clicks, cost",
    [(datetime.date(2000, 1, 1), 100, 200, 300)],
)
def test_create_statistics_unique_violation_exception(
    db: Session, date: datetime.date, views: int, clicks: int, cost: float
) -> None:
    """Tests an error when trying to re-write a statistics with the same date."""
    statistics_in = schemas.Statistics(
        date=date, views=views, clicks=clicks, cost=cost
    )
    create_statistics(db, statistics=statistics_in)
    with pytest.raises(UniqueViolationException):
        create_statistics(db, statistics=statistics_in)


@pytest.mark.parametrize(
    "date, views, clicks, cost",
    [(datetime.date(2000, 1, 1), 100, 200, 300)],
)
def test_get_existent_statistics_for_date(
    db: Session, date: datetime.date, views: int, clicks: int, cost: float
) -> None:
    """Test getting statistics from db when object with input data is in db."""
    statistics_in = schemas.Statistics(
        date=date, views=views, clicks=clicks, cost=cost
    )
    created_statistic = create_statistics(db, statistics=statistics_in)
    received_statistic = get_statistics_for_date(db, statistics_date=date)

    assert received_statistic
    assert jsonable_encoder(received_statistic) == jsonable_encoder(created_statistic)
    assert received_statistic.date == created_statistic.date


@pytest.mark.parametrize("date", [datetime.date(2000, 1, 1)])
def test_get_nonexistent_statistics_for_date(db: Session, date: datetime.date) -> None:
    """Test getting statistics from db when there is not object
    with input data in db.
    """
    received_statistic = get_statistics_for_date(db, statistics_date=date)
    assert not received_statistic


def test_get_statistics_for_date_period_without_conditions(
    db_with_data: Session
) -> None:
    """Test getting statistics for date period without
    'date_from' and 'date_to' parameters. All objects in results.
    """
    statistics = get_statistics_for_date_period(db_with_data)
    assert len(statistics) == STATISTICS_LIST_LEN


@pytest.mark.parametrize(
    "date_from",
    [datetime.date(2000, 1, 1), datetime.date(2000, 1, 2), datetime.date(2000, 1, 3)]
)
def test_get_statistics_for_date_period_with_date_from_date_in_range(
    db_with_data: Session, date_from: datetime.date
) -> None:
    """Test getting statistics for date period with 'date_from' but
     without 'date_to' parameters. 'date_from' have value from date range that in db.
    """
    statistics = get_statistics_for_date_period(db_with_data, date_from=date_from)
    assert len(statistics) == STATISTICS_LIST_LEN - date_from.day + 1


@pytest.mark.parametrize("date_from", [datetime.date(1999, 12, 31)])
def test_get_statistics_for_date_period_with_date_from_date_less_range(
    db_with_data: Session, date_from: datetime.date
) -> None:
    """Test getting statistics for date period with 'date_from' but
     without 'date_to' parameters. 'date_from' have value less them the smallest
     date value from db. All objects in results.
    """
    statistics = get_statistics_for_date_period(db_with_data, date_from=date_from)
    assert len(statistics) == STATISTICS_LIST_LEN


@pytest.mark.parametrize("date_from", [datetime.date(2000, 1, STATISTICS_LIST_LEN + 1)])
def test_get_statistics_for_date_period_with_date_from_date_more_range(
    db_with_data: Session, date_from: datetime.date
) -> None:
    """Test getting statistics for date period with 'date_from' but
     without 'date_to' parameters. 'date_from' have value more them the most
     date value from db. There are not objects in results.
    """
    statistics = get_statistics_for_date_period(db_with_data, date_from=date_from)
    assert len(statistics) == 0


@pytest.mark.parametrize(
    "date_to",
    [datetime.date(2000, 1, 1), datetime.date(2000, 1, 2), datetime.date(2000, 1, 3)]
)
def test_get_statistics_for_date_period_with_date_to_date_in_range(
    db_with_data: Session, date_to: datetime.date
) -> None:
    """Test getting statistics for date period with 'date_to' but
     without 'date_from' parameters. 'date_to' have value from date range that in db.
    """
    statistics = get_statistics_for_date_period(db_with_data, date_to=date_to)
    assert len(statistics) == date_to.day


@pytest.mark.parametrize("date_to", [datetime.date(1999, 12, 31)])
def test_get_statistics_for_date_period_with_date_to_date_less_range(
    db_with_data: Session, date_to: datetime.date
) -> None:
    """Test getting statistics for date period with 'date_to' but
     without 'date_from' parameters. 'date_to' have value less them the smallest
     date value from db. There are not objects in results.
    """
    statistics = get_statistics_for_date_period(db_with_data, date_to=date_to)
    assert len(statistics) == 0


@pytest.mark.parametrize("date_to", [datetime.date(2000, 1, STATISTICS_LIST_LEN + 1)])
def test_get_statistics_for_date_period_with_date_to_date_more_range(
    db_with_data: Session, date_to: datetime.date
) -> None:
    """Test getting statistics for date period with 'date_to' but
     without 'date_from' parameters. 'date_to' have value more them the most
     date value from db. All objects in results.
    """
    statistics = get_statistics_for_date_period(db_with_data, date_to=date_to)
    assert len(statistics) == STATISTICS_LIST_LEN


@pytest.mark.parametrize(
    "date_from, date_to, result_len",
    [

        (datetime.date(1999, 12, 1), datetime.date(1999, 12, 31), 0),
        (datetime.date(1999, 12, 31), datetime.date(2000, 1, 1), 1),
        (datetime.date(1999, 12, 31), datetime.date(2000, 1, 2), 2),
        (datetime.date(1999, 12, 31), datetime.date(2000, 1, 3), 3),
        (
            datetime.date(1999, 12, 31),
            datetime.date(2000, 1, STATISTICS_LIST_LEN + 1), 3
        ),
        (datetime.date(2000, 1, 1), datetime.date(2000, 1, 1), 1),
        (datetime.date(2000, 1, 1), datetime.date(2000, 1, 2), 2),
        (datetime.date(2000, 1, 1), datetime.date(2000, 1, 3), 3),
        (datetime.date(2000, 1, 1), datetime.date(2000, 1, STATISTICS_LIST_LEN + 1), 3),
        (datetime.date(2000, 1, 2), datetime.date(2000, 1, 3), 2),
        (datetime.date(2000, 1, 2), datetime.date(2000, 1, STATISTICS_LIST_LEN + 1), 2),
        (datetime.date(2000, 1, 3), datetime.date(2000, 1, STATISTICS_LIST_LEN + 1), 1),
        (
            datetime.date(2000, 1, STATISTICS_LIST_LEN + 1),
            datetime.date(2000, 1, STATISTICS_LIST_LEN + 2), 0
        ),
    ]
)
def test_get_statistics_for_date_period_with_both_conditions(
    db_with_data: Session, date_from: datetime.date,
    date_to: datetime.date, result_len: int
) -> None:
    """Test getting statistics for date period with both parameters
    'date_to' and 'date_from'. All situations.
     """
    statistics = get_statistics_for_date_period(
        db_with_data, date_from=date_from, date_to=date_to
    )
    assert len(statistics) == result_len


@pytest.mark.parametrize(
    "date, for_sum",
    [(datetime.date(2000, 1, 1), 0), (datetime.date(2000, 1, 1), 100)]
)
def test_summarize_statistics(db: Session, date: datetime.date, for_sum: int) -> None:
    """Testing summation of new data with data already available in the database."""
    statistics = schemas.Statistics(date=date, views=100, clicks=100, cost=100.0)
    old_statistics = models.Statistics(**statistics.dict())
    db.add(old_statistics)
    new_statistics = summarize_statistics(
        db, statistics, views=for_sum, clicks=for_sum, cost=for_sum
    )
    assert old_statistics.date == new_statistics.date
    assert old_statistics.views + for_sum == new_statistics.views
    assert old_statistics.cost + for_sum == new_statistics.cost
    assert old_statistics.clicks + for_sum == new_statistics.clicks


def test_delete_all_statistics(db_with_data: Session) -> None:
    """Testing the deletion of all statistics from database."""
    assert db_with_data.query(models.Statistics).count() == STATISTICS_LIST_LEN
    delete_all_statistics(db_with_data)
    assert db_with_data.query(models.Statistics).count() == 0


@pytest.mark.parametrize(
    "date, old_val, new_val",
    [(datetime.date(2000, 1, 1), 100, 10)]
)
def test_summarize_or_create_statistics_data_exists(
    db: Session, date: datetime.date, old_val: int, new_val: int
) -> None:
    """Test function when the data already exists and will not be created again.
    The data will be combined with the existing ones.
    """
    old_stat = schemas.Statistics(
        date=date, views=old_val, clicks=old_val, cost=old_val
    )
    new_stat = schemas.Statistics(
        date=date, views=new_val, clicks=new_val, cost=new_val
    )
    old_statistics = models.Statistics(**old_stat.dict())
    db.add(old_statistics)
    db.commit()

    new_statistics, created = summarize_or_create_statistics(db, new_stat)
    assert created is False
    assert new_statistics.date == old_statistics.date
    assert new_statistics.views == old_stat.views + new_val
    assert new_statistics.clicks == old_stat.clicks + new_val
    assert new_statistics.cost == old_stat.cost + new_val


@pytest.mark.parametrize(
    "date, val",
    [(datetime.date(2000, 1, 1), 100)]
)
def test_summarize_or_create_statistics_data_not_exists(
    db: Session, date: datetime.date, val: int
) -> None:
    """Test function when the data does not exist yet and it will be created."""
    new_statistics = schemas.Statistics(date=date, views=val, clicks=val, cost=val)

    statistics, created = summarize_or_create_statistics(db, new_statistics)
    assert created
    assert jsonable_encoder(models.Statistics(**new_statistics.dict())) == \
           jsonable_encoder(statistics)
