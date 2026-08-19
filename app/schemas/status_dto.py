from pydantic import BaseModel


class StatusDTO(BaseModel):
    status: str