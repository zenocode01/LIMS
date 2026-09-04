from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./lims.db"
    jwt_secret: str = "change-me"
    jwt_expire_min: int = 720


@lru_cache
def get_settings() -> Settings:
    return Settings()
