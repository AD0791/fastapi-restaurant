from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["development", "staging", "production"]


class Settings(BaseSettings):
    environment: Environment
    api_base_url: str = "http://localhost:8000"
    port: int = 8000

    # pydantic-settings defaults to extra="forbid"; .env is shared with the mysql image's own
    # entrypoint, which reads keys this class never will, so unknown keys are tolerated here
    # rather than treated as a misconfiguration.
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")
