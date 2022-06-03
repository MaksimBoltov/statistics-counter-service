from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from .settings import get_db_settings

db_settings = get_db_settings()
SQLALCHEMY_DATABASE_URL = (
    f"{db_settings.engine}://{db_settings.user}:{db_settings.password}@"
    f"{db_settings.host}:{db_settings.port}/{db_settings.database}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Session:
    """Returns a session for the database."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
