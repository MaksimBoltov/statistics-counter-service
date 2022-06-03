from functools import lru_cache

from pydantic import BaseSettings


class DatabaseSettings(BaseSettings):
    engine: str
    user: str
    password: str
    host: str
    port: str
    database: str

    class Config:
        env_prefix = "DB_"
        env_file = ".env"


@lru_cache
def get_db_settings() -> DatabaseSettings:
    """Returns the database configuration object from the environment file."""
    return DatabaseSettings()
