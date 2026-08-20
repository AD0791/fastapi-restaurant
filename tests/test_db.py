from collections.abc import AsyncIterator
from typing import Any

from fastapi.testclient import TestClient

from app.deps import get_session
from main import app as main_app


class _FakeSession:
    def __init__(self, *, should_fail: bool) -> None:
        self._should_fail = should_fail

    async def execute(self, statement: Any) -> None:
        if self._should_fail:
            raise ConnectionRefusedError("database unreachable")


def _override_session(*, should_fail: bool):
    async def _get_session() -> AsyncIterator[_FakeSession]:
        yield _FakeSession(should_fail=should_fail)

    return _get_session


def test_ready_returns_ready_body_when_database_answers() -> None:
    main_app.dependency_overrides[get_session] = _override_session(should_fail=False)
    try:
        with TestClient(main_app) as client:
            response = client.get("/ready")
    finally:
        del main_app.dependency_overrides[get_session]

    assert response.status_code == 200
    assert response.json() == {"status": "ready", "database": "ok"}


def test_ready_returns_problem_body_when_database_unreachable() -> None:
    main_app.dependency_overrides[get_session] = _override_session(should_fail=True)
    try:
        with TestClient(main_app) as client:
            response = client.get("/ready", headers={"X-Request-ID": "demo-503"})
    finally:
        del main_app.dependency_overrides[get_session]

    assert response.status_code == 503
    assert response.headers["content-type"] == "application/problem+json"
    body = response.json()
    assert body["code"] == "ERR_SERVICE_UNAVAILABLE"
    assert body["request_id"] == "demo-503"


def test_openapi_documents_the_503_problem_response() -> None:
    responses = main_app.openapi()["paths"]["/ready"]["get"]["responses"]

    assert responses["503"]["content"]["application/problem+json"] == {}
