from typing import Annotated, Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["development", "staging", "production"]


class Settings(BaseSettings):
    environment: Environment
    api_base_url: str = "http://localhost:8000"
    port: int = 8000
    log_level: str = "info"
    database_url: str
    database_pool_size: Annotated[int, Field(ge=1, le=20)] = 5
    database_ssl_ca_path: str = ""

    # pydantic-settings defaults to extra="forbid"; .env is shared with the mysql image's own
    # entrypoint, which reads keys this class never will, so unknown keys are tolerated here
    # rather than treated as a misconfiguration.
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")
