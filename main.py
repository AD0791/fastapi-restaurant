from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated

import structlog
from fastapi import Depends, FastAPI, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.config import Settings
from app.db import make_engine
from app.deps import get_session
from app.logging import add_request_id_middleware, configure_logging
from app.schemas.config_dto import ConfigDTO
from app.schemas.problem_dto import ProblemDTO
from app.schemas.ready_dto import ReadyDTO
from app.schemas.status_dto import StatusDTO

settings = Settings()
configure_logging(settings)


def create_app(settings: Settings) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
        engine = make_engine(settings)
        app.state.session_factory = async_sessionmaker(engine, expire_on_commit=False)
        yield
        await engine.dispose()

    app = FastAPI(lifespan=lifespan)
    add_request_id_middleware(app)

    @app.get("/health", response_model=StatusDTO, status_code=status.HTTP_200_OK)
    async def health() -> StatusDTO:
        return StatusDTO(status="ok")

    @app.get("/config", response_model=ConfigDTO, status_code=status.HTTP_200_OK)
    async def config() -> ConfigDTO:
        return ConfigDTO(
            api_base_url=settings.api_base_url,
            environment=settings.environment
        )

    @app.get(
        "/ready",
        response_model=ReadyDTO,
        status_code=status.HTTP_200_OK,
        responses={
            status.HTTP_503_SERVICE_UNAVAILABLE: {
                "model": ProblemDTO,
                "description": "The database did not answer.",
                "content": {"application/problem+json": {}},
            }
        },
    )
    async def ready(session: Annotated[AsyncSession, Depends(get_session)]) -> ReadyDTO | JSONResponse:
        try:
            await session.execute(text("SELECT 1"))
        except Exception:
            problem = ProblemDTO(
                type="about:blank",
                title="Service unavailable",
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
                code="ERR_SERVICE_UNAVAILABLE",
                detail="database unreachable",
                request_id=structlog.contextvars.get_contextvars().get("request_id"),
            )
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                media_type="application/problem+json",
                content=problem.model_dump(),
            )
        return ReadyDTO(status="ready", database="ok")

    return app


app = create_app(settings)
