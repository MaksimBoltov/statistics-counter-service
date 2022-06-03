import os

from dotenv import load_dotenv

from app.settings import get_db_settings


def test_database_settings() -> None:
    """Testing the correct unloading of data from environment variables."""
    db_settings = get_db_settings()
    load_dotenv()
    assert db_settings.engine == os.getenv("DB_ENGINE")
    assert db_settings.user == os.getenv("DB_USER")
    assert db_settings.password == os.getenv("DB_PASSWORD")
    assert db_settings.host == os.getenv("DB_HOST")
    assert db_settings.port == os.getenv("DB_PORT")
    assert db_settings.database == os.getenv("DB_DATABASE")
