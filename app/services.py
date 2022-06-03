from typing import Optional

from . import models, schemas


def _get_cpc(cost: float, clicks: int) -> Optional[float]:
    """Returns the average cost per click."""
    if clicks == 0:
        return None
    return round(cost / clicks, 2)


def _get_cpm(cost: float, views: int) -> Optional[float]:
    """Returns the average cost per 1000 views."""
    if views == 0:
        return None
    return round(cost / views * 1000, 2)


def get_returns_statistics(
    statistics: list[models.Statistics], sort_by: str = None, reverse_sort: bool = False
) -> dict:
    """Returns statistics in the form of a dictionary that has the form (example):
    {
        '2000-01-01': {
            'date': '2000-01-01',
            'views': 1000,
            'clicks': 2500,
            'cost': 500.00,
            'cpc': 0.2,
            'cpm': 500.0
        }
    }
    """

    reformed_statistics = dict()
    for stat in statistics:
        reformed_statistics[stat.date] = dict(schemas.Statistics.from_orm(stat))
        reformed_statistics[stat.date]["cpc"] = _get_cpc(stat.cost, stat.clicks)
        reformed_statistics[stat.date]["cpm"] = _get_cpm(stat.cost, stat.views)

    # If param sort_by is not entered or entered incorrectly,
    # then sort_by = 'date' is used by default
    if len(reformed_statistics) == 0 or \
            sort_by not in list(reformed_statistics.values())[0].keys():
        return dict(sorted(
            reformed_statistics.items(),
            key=lambda x: x[0], reverse=reverse_sort
        ))

    return dict(sorted(
        reformed_statistics.items(),
        key=lambda x: x[1][sort_by], reverse=reverse_sort
    ))
