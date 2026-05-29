import pytest

from app.core.config import Settings
from app.core.database import init_database
from app.services.alert_dispatch import dispatch_region_alerts
from app.services.repository import create_subscription


@pytest.mark.asyncio
async def test_dispatch_region_alerts_dry_run_records_event(tmp_path) -> None:
    settings = Settings(
        app_env="test",
        database_url=f"sqlite:///{tmp_path / 'whereitfalls.db'}",
    )
    assert init_database(settings) is True
    subscription = create_subscription(
        settings,
        channel="email",
        region="DF",
        min_score=0.1,
        email="ops@example.com",
    )
    assert subscription is not None

    first = await dispatch_region_alerts(settings, dry_run=True, min_score=0.1)
    second = await dispatch_region_alerts(settings, dry_run=True, min_score=0.1)

    assert first.evaluated >= 1
    assert first.matched >= 1
    assert first.sent == 0
    assert first.events[0].status == "dry_run"
    assert second.events[0].status == "duplicate"
