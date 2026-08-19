from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_config_returns_exactly_two_fields() -> None:
    response = client.get("/config")

    assert response.status_code == 200
    assert response.json().keys() == {"api_base_url", "environment"}


def test_health_still_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_names_the_response_schemas() -> None:
    schemas = app.openapi()["components"]["schemas"]

    assert "ConfigDTO" in schemas
    assert "StatusDTO" in schemas
    assert set(schemas["ConfigDTO"]["properties"]) == {"api_base_url", "environment"}


def test_openapi_environment_carries_the_enum() -> None:
    schemas = app.openapi()["components"]["schemas"]

    assert schemas["ConfigDTO"]["properties"]["environment"]["enum"] == [
        "development",
        "staging",
        "production",
    ]
