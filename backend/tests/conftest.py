import pytest

from app.core.config import get_settings
from app.core.database import get_engine
from app.services.repository import clear_memory_store


@pytest.fixture(autouse=True)
def isolate_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("SPACETRACK_USER", "")
    monkeypatch.setenv("SPACETRACK_PASS", "")
    get_settings.cache_clear()
    get_engine.cache_clear()
    clear_memory_store()
    yield
    get_settings.cache_clear()
    get_engine.cache_clear()
    clear_memory_store()
