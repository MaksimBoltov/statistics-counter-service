from sqlalchemy import Column, Date, Float, Integer

from .database import Base


class Statistics(Base):
    """The model of statistics. Statistics are stored by date."""
    __tablename__ = "statistic"

    date = Column(Date, primary_key=True, index=True, unique=True)
    views = Column(Integer, nullable=False)
    clicks = Column(Integer, nullable=False)
    cost = Column(Float, nullable=False)
