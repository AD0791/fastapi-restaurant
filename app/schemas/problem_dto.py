from pydantic import BaseModel


class ProblemDTO(BaseModel):
    type: str
    title: str
    status: int
    code: str
    detail: str | None = None
    request_id: str | None = None
