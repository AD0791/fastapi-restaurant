from pydantic import BaseModel

from app.config import Environment


class ConfigDTO(BaseModel):
    api_base_url: str
    environment: Environment
