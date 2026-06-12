from functools import lru_cache

from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ALRSCRM API"
    environment: str = "local"
    debug: bool = Field(default=False, validation_alias="APP_DEBUG")
    api_v1_prefix: str = "/api/v1"

    secret_key: str | None = Field(default=None, validation_alias="SECRET_KEY")
    database_url: str = Field(default="postgresql+psycopg://alrscrm:alrscrm@localhost:5432/alrscrm")
    database_pool_size: int = 5
    database_max_overflow: int = 10
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret_key: str = Field(
        default="change-this-secret-in-production",
        validation_alias=AliasChoices("JWT_SECRET_KEY", "JWT_SECRET"),
    )
    integration_encryption_key: str | None = None
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 7
    storage_provider: str = "local"
    storage_signed_url_expire_seconds: int = 900
    do_spaces_region: str | None = None
    do_spaces_bucket: str | None = None
    do_spaces_access_key: str | None = None
    do_spaces_secret_key: str | None = None
    do_spaces_endpoint_url: str | None = None
    do_spaces_cdn_url: str | None = None
    do_spaces_path_prefix: str = "alrscrm"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @model_validator(mode="after")
    def validate_security_settings(self) -> "Settings":
        non_local = self.environment.lower() not in {"local", "test", "development"}
        if non_local:
            self._validate_secret("SECRET_KEY", self.secret_key)
            self._validate_secret("JWT_SECRET", self.jwt_secret_key)
            self._validate_secret("INTEGRATION_ENCRYPTION_KEY", self.integration_encryption_key)
        if self.access_token_expire_minutes <= 0 or self.refresh_token_expire_minutes <= 0:
            raise ValueError("Token expiry settings must be positive")
        if self.storage_signed_url_expire_seconds <= 0:
            raise ValueError("Storage signed URL expiry must be positive")
        if self.storage_provider.lower() in {"digitalocean", "spaces", "do_spaces"}:
            missing = [
                name
                for name, value in {
                    "DO_SPACES_REGION": self.do_spaces_region,
                    "DO_SPACES_BUCKET": self.do_spaces_bucket,
                    "DO_SPACES_ACCESS_KEY": self.do_spaces_access_key,
                    "DO_SPACES_SECRET_KEY": self.do_spaces_secret_key,
                }.items()
                if not value
            ]
            if missing:
                raise ValueError(f"Missing DigitalOcean Spaces settings: {', '.join(missing)}")
        return self

    @staticmethod
    def _validate_secret(name: str, value: str | None) -> None:
        if value is None or not value.strip():
            raise ValueError(f"{name} is required in production")
        stripped = value.strip()
        insecure_values = {
            "change-this-secret-in-production",
            "replace-with-a-strong-secret",
            "secret",
            "password",
        }
        if stripped in insecure_values or len(stripped) < 32 or len(set(stripped)) < 8:
            raise ValueError(f"{name} must have at least 32 characters of entropy")


@lru_cache
def get_settings() -> Settings:
    return Settings()
