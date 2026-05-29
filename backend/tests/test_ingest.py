from datetime import UTC, datetime

from app.services.ingest import _normalize_lon, _parse_spacetrack_datetime


def test_parse_spacetrack_datetime_as_utc() -> None:
    assert _parse_spacetrack_datetime("2026-05-28 03:00:00") == datetime(
        2026,
        5,
        28,
        3,
        0,
        tzinfo=UTC,
    )


def test_parse_spacetrack_datetime_handles_missing_value() -> None:
    assert _parse_spacetrack_datetime(None) is None


def test_normalize_lon_to_wgs84_range() -> None:
    assert _normalize_lon(347.8) == -12.2
    assert _normalize_lon(163.1) == 163.1
