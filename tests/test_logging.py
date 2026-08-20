import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.logging import add_request_id_middleware
from main import app as main_app

client = TestClient(main_app)


def test_request_produces_one_structured_line(capsys: pytest.CaptureFixture[str]) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    lines = capsys.readouterr().out.strip().splitlines()
    assert len(lines) == 1
    parsed = json.loads(lines[0])
    assert parsed["event"] == "request.completed"
    assert {"event", "timestamp", "severity", "request_id"} <= parsed.keys()


def test_caller_supplied_request_id_is_echoed(capsys: pytest.CaptureFixture[str]) -> None:
    response = client.get("/health", headers={"X-Request-ID": "demo-123"})

    assert response.headers["x-request-id"] == "demo-123"
    line = capsys.readouterr().out.strip().splitlines()[-1]
    assert json.loads(line)["request_id"] == "demo-123"


def test_failing_request_logs(capsys: pytest.CaptureFixture[str]) -> None:
    app = FastAPI()
    add_request_id_middleware(app)

    @app.get("/boom")
    async def boom() -> None:
        raise RuntimeError("boom")

    boom_client = TestClient(app)

    with pytest.raises(RuntimeError):
        boom_client.get("/boom")

    line = capsys.readouterr().out.strip().splitlines()[-1]
    assert json.loads(line)["event"] == "request.failed"
