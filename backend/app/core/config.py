from functools import lru_cache

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ALRSCRM API"
    environment: str = "local"
    debug: bool = Field(default=False, validation_alias="APP_DEBUG")
    api_v1_prefix: str = "/api/v1"

    database_url: str = Field(
        default="postgresql+psycopg://alrscrm:alrscrm@localhost:5432/alrscrm"
    )
    database_pool_size: int = 5
    database_max_overflow: int = 10
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret_key: str = "change-this-secret-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 7

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @model_validator(mode="after")
    def validate_security_settings(self) -> "Settings":
        non_local = self.environment.lower() not in {"local", "test", "development"}
        insecure_secret = self.jwt_secret_key == "change-this-secret-in-production"
        if non_local and (insecure_secret or len(self.jwt_secret_key) < 32):
            raise ValueError("JWT_SECRET_KEY must be a strong non-default secret")
        if self.access_token_expire_minutes <= 0 or self.refresh_token_expire_minutes <= 0:
            raise ValueError("Token expiry settings must be positive")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
