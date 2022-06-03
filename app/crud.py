from datetime import date
from typing import Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from . import models, schemas
from .exceptions import UniqueViolationException


def get_statistics_for_date(
    db: Session, statistics_date: date
) -> Optional[models.Statistics]:
    """Returns all statistics for a specific date or returns None
    if there are no statistics in the database for the specific date.
    """
    return db.query(models.Statistics).filter(
        models.Statistics.date == statistics_date
    ).first()


def get_statistics_for_date_period(
    db: Session, date_from: date = None, date_to: date = None,
) -> list[models.Statistics]:
    """Returns all statistics for a certain date period.
    Parameters 'date_from' and 'date_to' are included in the selection.

    Situations:

    - If both parameters are entered, then statistics from 'date_from' (including) to
      'date_to' (including) are returned
    - If only 'date_from' is entered, then all statistics starting from
      'date_from' (inclusive) are returned
    - If only 'date_to' is entered, then all statistics up to
      'date_to' (inclusive) are returned
    - If both parameters 'date_from' and 'date_to' are omitted then
      all available statistics in the database are returned
    """
    # Defining a list of conditions for statistics search
    search_expressions = []
    if date_from:
        search_expressions.append(models.Statistics.date >= date_from)
    if date_to:
        search_expressions.append(models.Statistics.date <= date_to)

    return db.query(models.Statistics).filter(and_(True, *search_expressions)).all()


def create_statistics(db: Session, statistics: schemas.Statistics) -> models.Statistics:
    """Creates an instance of statistics in the database if there were no
    statistics for this date or raises an exception UniqueViolationException.
    """
    # If an object with the same date is already in the database,
    # then raise an exception
    if get_statistics_for_date(db, statistics.date):
        raise UniqueViolationException

    new_statistics = models.Statistics(**statistics.dict())
    db.add(new_statistics)
    db.commit()
    db.refresh(new_statistics)

    return new_statistics


def summarize_statistics(
    db: Session, statistics: models.Statistics,
    views: int = 0, clicks: int = 0, cost: float = .0
) -> models.Statistics:
    """Adds values to statistics and returns an updated object."""
    statistics.views += views
    statistics.clicks += clicks
    statistics.cost += cost
    db.commit()

    return statistics


def summarize_or_create_statistics(
    db: Session, statistics: schemas.Statistics
) -> tuple[models.Statistics, bool]:
    """Adds statistics data to the database if there are no statistics for the
    input date in the database or adds indicators to the available values.
    Returns the statistics object and the value True if the object was created
    and the value False if the object was already in the database.
    """

    received_statistics = get_statistics_for_date(db, statistics.date)

    # If there are no statistics for this date in the database, create a new object
    if not received_statistics:
        created_statistics = create_statistics(db, statistics)
        return created_statistics, True

    # If there are statistics for this date, summarize values
    updated_statistics = summarize_statistics(
        db, received_statistics,
        views=statistics.views,
        clicks=statistics.clicks,
        cost=statistics.cost
    )

    return updated_statistics, False


def delete_all_statistics(db: Session) -> None:
    """Clears all statistics from the database."""
    db.query(models.Statistics).delete()
    db.commit()
