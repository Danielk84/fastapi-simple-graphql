import secrets

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import MongoDsn, Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    DEBUG: bool = True
    ORIGINS: list = ["http://127.0.0.1:8000/",]
    mongo_dsn: MongoDsn = 'xxx'

    SECRET_KEY: str = Field(secrets.token_urlsafe(64))
    TOKEN_ALGORITHM: str = "HS256"

    # Time by minutes
    TOKEN_EXPIRED_TIME: int = 20


settings = Settings()
