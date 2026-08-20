from typing import Literal

from pydantic import BaseModel


class ReadyDTO(BaseModel):
    status: Literal["ready"]
    database: Literal["ok"]
