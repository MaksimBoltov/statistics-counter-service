import datetime

from pydantic import BaseModel, validator
from pydantic.types import NonNegativeInt, NonNegativeFloat


class Statistics(BaseModel):
    date: datetime.date
    views: NonNegativeInt = 0
    clicks: NonNegativeInt = 0
    cost: NonNegativeFloat = .0

    @validator("cost")
    def round_cost(cls, v):
        return round(v, 2)

    class Config:
        orm_mode = True
