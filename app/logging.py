import uuid
from collections.abc import Awaitable, Callable

import structlog
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response

from app.config import Settings


def configure_logging(settings: Settings) -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.add_log_level,
            _rename_level_to_severity,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(settings.log_level),
        cache_logger_on_first_use=True,
    )


def _rename_level_to_severity(logger, method_name, event_dict):
    event_dict["severity"] = event_dict.pop("level", method_name).upper()
    return event_dict


def add_request_id_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def add_request_id(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        structlog.contextvars.bind_contextvars(request_id=request_id)
        try:
            response = await call_next(request)
        except Exception:
            structlog.get_logger().exception(
                "request.failed",
                method=request.method,
                path=request.url.path,
            )
            raise
        else:
            response.headers["X-Request-ID"] = request_id
            structlog.get_logger().info(
                "request.completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
            )
            return response
        finally:
            structlog.contextvars.clear_contextvars()
