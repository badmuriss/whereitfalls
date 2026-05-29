from datetime import UTC, datetime

from app.core.config import Settings
from app.core.database import init_database
from app.models.domain import Confidence, ObjectType
from app.services.ingest import ReentryCandidate, ReentrySource
from app.services.repository import (
    count_risk_corridors,
    create_subscription,
    list_stored_reentry_candidates,
    list_subscriptions,
    record_alert_event,
    upsert_reentry_candidates,
    upsert_risk_corridor,
)


def test_upsert_reentry_candidates_is_idempotent(tmp_path) -> None:
    settings = Settings(
        app_env="test",
        database_url=f"sqlite:///{tmp_path / 'whereitfalls.db'}",
    )
    assert init_database(settings) is True
    candidate = ReentryCandidate(
        prediction_id="st-tip-test-20260530T020400Z",
        norad_id=46335,
        name="STARLINK-1727",
        type=ObjectType.payload,
        country="US",
        predicted_reentry_utc=datetime(2026, 5, 30, 2, 4, tzinfo=UTC),
        uncertainty_minutes=1440,
        predicted_lat=28.2,
        predicted_lon=163.1,
        confidence=Confidence.low,
        max_region_score=0.25,
        tle=("1 46335U 20062L", "2 46335 53.0248"),
        source=ReentrySource.spacetrack,
    )

    first = upsert_reentry_candidates(settings, [candidate])
    second = upsert_reentry_candidates(settings, [candidate])
    stored = list_stored_reentry_candidates(settings)

    assert first.available is True
    assert second.available is True
    assert first.stored == 1
    assert second.stored == 1
    assert len(stored) == 1
    assert stored[0].name == "STARLINK-1727"
    assert stored[0].tle == candidate.tle


def test_upsert_risk_corridor_is_idempotent(tmp_path) -> None:
    settings = Settings(
        app_env="test",
        database_url=f"sqlite:///{tmp_path / 'whereitfalls.db'}",
    )
    assert init_database(settings) is True
    corridor = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": []},
                "properties": {},
            }
        ],
    }

    first = upsert_risk_corridor(settings, "prediction-1", corridor, 0.8)
    second = upsert_risk_corridor(settings, "prediction-1", corridor, 0.7)

    assert first.available is True
    assert second.available is True
    assert count_risk_corridors(settings) == 1


def test_subscription_and_alert_event_persistence(tmp_path) -> None:
    settings = Settings(
        app_env="test",
        database_url=f"sqlite:///{tmp_path / 'whereitfalls.db'}",
    )
    assert init_database(settings) is True
    subscription = create_subscription(
        settings,
        channel="email",
        region="df",
        min_score=0.4,
        email="ops@example.com",
    )
    assert subscription is not None
    assert subscription.id is not None
    event = record_alert_event(
        settings,
        prediction_id="p1",
        subscription_id=subscription.id,
        region="df",
        score=0.7,
        status="dry_run",
    )
    duplicate = record_alert_event(
        settings,
        prediction_id="p1",
        subscription_id=subscription.id,
        region="DF",
        score=0.7,
        status="dry_run",
    )

    assert list_subscriptions(settings)[0].region == "DF"
    assert event.available is True
    assert duplicate.duplicate is True
