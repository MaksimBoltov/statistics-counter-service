from datetime import date

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from . import schemas
from .crud import (
    delete_all_statistics,
    get_statistics_for_date_period,
    summarize_or_create_statistics
)
from .database import get_db
from .services import get_returns_statistics

router = APIRouter()


@router.get("/statistics")
def get_statistics(
    date_from: date = None, date_to: date = None,
    sort_by: str = None, reverse_sort: bool = False,
    db: Session = Depends(get_db)
):
    """Returns all statistics in the range from 'date_from' (inclusive) to
    'date_to' (inclusive).

    Cases:

    - If 'date_from' is not specified, then all statistics up to
      'date_to' (inclusive) are shown.
    - If 'date_to' is not specified, then all statistics are shown starting from
      'date_from' (inclusive).
    - If both parameters are omitted, then all existing statistics are shown.
    """
    statistics = get_statistics_for_date_period(db, date_from, date_to)
    return get_returns_statistics(statistics, sort_by, reverse_sort)


@router.post("/statistics")
def save_statistics(statistics: schemas.Statistics, db: Session = Depends(get_db)):
    """Processes the saving of new statistics to the database.
    If there are statistics for the entered date, the statistics will be summarized.
    """
    statistics, created = summarize_or_create_statistics(db, statistics)
    content = {
        "statistics": {
            "date": str(statistics.date),
            "views": statistics.views,
            "clicks": statistics.clicks,
            "cost": statistics.cost,
        },
        "created": created,
        "aggregated": not created,
    }
    return JSONResponse(status_code=201, content=content)


@router.delete("/statistics")
def reset_statistics(db: Session = Depends(get_db)):
    """Deletes all saved statistics."""
    delete_all_statistics(db)
    return {"message": "Deleted", "error": 0}
