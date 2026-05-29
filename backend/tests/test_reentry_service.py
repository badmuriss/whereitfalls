import asyncio

import pytest

from app.core.config import Settings
from app.services.ingest import SpaceTrackClient
from app.services.reentries import ReentryService


@pytest.mark.asyncio
async def test_live_rows_coalesces_parallel_spacetrack_fetches(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = ReentryService()
    settings = Settings(app_env="local", spacetrack_user="user", spacetrack_pass="pass")
    fake_rows = service._demo_rows()
    calls = 0

    async def fake_fetch(
        self: SpaceTrackClient,
        limit: int = 6,
    ) -> list:
        nonlocal calls
        calls += 1
        await asyncio.sleep(0.01)
        return fake_rows

    monkeypatch.setattr(SpaceTrackClient, "fetch_reentry_candidates", fake_fetch)
    monkeypatch.setattr("app.services.reentries.upsert_reentry_candidates", lambda *_: None)

    results = await asyncio.gather(
        service._live_rows(settings, limit=8),
        service._live_rows(settings, limit=8),
        service._live_rows(settings, limit=8),
    )

    assert calls == 1
    assert all(result == fake_rows[:8] for result in results)
