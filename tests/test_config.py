import pytest
from pydantic import ValidationError

from app.config import Settings


def test_missing_environment_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ENVIRONMENT", raising=False)

    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None)

    assert "environment" in str(exc_info.value)


def test_settings_constructs_with_types(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENVIRONMENT", "development")

    settings = Settings(_env_file=None)

    assert settings.environment == "development"
    assert isinstance(settings.api_base_url, str)
    assert isinstance(settings.port, int)
