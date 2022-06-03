import os
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def db():
    """Returns the session object for testing.
    After completion, deletes the test database.
    """
    database_file = "test.db"
    SQLALCHEMY_DATABASE_URL = f"sqlite:///./{database_file}"

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = Session(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)

    try:
        yield TestingSessionLocal
    finally:
        TestingSessionLocal.close()
        if Path(database_file).exists():
            os.remove(database_file)


@pytest.fixture()
def db_handlers():
    """Returns the session object for testing handlers.
    After completion, deletes the test database.
    """
    database_file = "test.db"
    SQLALCHEMY_DATABASE_URL = f"sqlite:///./{database_file}"

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
            if Path(database_file).exists():
                os.remove(database_file)

    app.dependency_overrides[get_db] = override_get_db
