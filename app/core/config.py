import os

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PrincipalConfig(BaseSettings):
    org_id: int
    roles: list[str] = []
    scopes: list[str] = []


class Settings(BaseSettings):
    # App
    service_name: str = "hrms"
    env: str = "local"

    # Database
    db_host: str
    db_port: int = 5432
    db_name: str
    db_user: str
    db_password: str

    @computed_field
    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    db_pool_min_size: int = 1
    db_pool_max_size: int = 10
    db_pool_timeout: int = 2

    # Rate limiting
    rate_limit_rpm: int = 120

    # Logging
    log_level: str = "INFO"

    # Auth
    api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"
        ),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
