from fastapi import FastAPI, status

from app.config import Settings
from app.schemas.config_dto import ConfigDTO
from app.schemas.status_dto import StatusDTO

settings = Settings()


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI()

    @app.get("/health", response_model=StatusDTO, status_code=status.HTTP_200_OK)
    async def health() -> StatusDTO:
        return StatusDTO(status="ok")

    @app.get("/config", response_model=ConfigDTO, status_code=status.HTTP_200_OK)
    async def config() -> ConfigDTO:
        return ConfigDTO(
            api_base_url=settings.api_base_url,
            environment=settings.environment
        )

    return app


app = create_app(settings)
