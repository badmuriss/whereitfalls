from datetime import UTC, datetime

from app.services.orbit import great_circle_distance_km, propagate_ground_track


def test_fallback_ground_track_is_centered_and_sized() -> None:
    points = propagate_ground_track(
        tle=None,
        epoch=datetime(2026, 6, 2, 14, 35, tzinfo=UTC),
        uncertainty_minutes=120,
        predicted_lat=-12.7,
        predicted_lon=-45.2,
        samples=12,
    )

    assert len(points) == 12
    assert min(lat for lat, _ in points) < -12.7
    assert max(lat for lat, _ in points) > -12.7
    assert all(-180 <= lon <= 180 for _, lon in points)


def test_great_circle_distance_for_same_point_is_zero() -> None:
    assert great_circle_distance_km((-15.8, -47.9), (-15.8, -47.9)) == 0
