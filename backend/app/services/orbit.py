from datetime import datetime, timedelta
from math import asin, atan2, cos, degrees, isfinite, radians, sin

try:
    from skyfield.api import EarthSatellite, load
except ImportError:  # pragma: no cover - exercised only without optional dependency
    EarthSatellite = None
    load = None


def _fallback_ground_track(
    center_lat: float,
    center_lon: float,
    uncertainty_minutes: int,
    samples: int,
) -> list[tuple[float, float]]:
    span = max(20, uncertainty_minutes / 2)
    points: list[tuple[float, float]] = []
    for index in range(samples):
        phase = (index / max(samples - 1, 1)) - 0.5
        lon = center_lon + phase * span * 2
        lat = center_lat + sin(phase * 3.14159 * 2) * 8
        points.append((round(lat, 4), round(((lon + 180) % 360) - 180, 4)))
    return points


def _subpoint_from_state(position_km: tuple[float, float, float]) -> tuple[float, float]:
    x, y, z = position_km
    if not all(isfinite(value) for value in (x, y, z)):
        raise ValueError("Satellite state produced non-finite coordinates.")
    lon = degrees(atan2(y, x))
    hyp = (x * x + y * y + z * z) ** 0.5
    if not isfinite(hyp) or hyp == 0:
        raise ValueError("Satellite state produced invalid radius.")
    lat = degrees(asin(z / hyp))
    if not isfinite(lat) or not isfinite(lon):
        raise ValueError("Satellite state produced non-finite lat/lon.")
    return round(lat, 4), round(lon, 4)


def propagate_ground_track(
    tle: tuple[str, str] | None,
    epoch: datetime,
    uncertainty_minutes: int,
    predicted_lat: float | None,
    predicted_lon: float | None,
    samples: int = 72,
) -> list[tuple[float, float]]:
    """Return `(lat, lon)` ground-track points for the uncertainty window.

    Skyfield is used when a valid TLE is available. Demo data may carry stale or
    synthetic TLEs, so failures fall back to a deterministic track centered on TIP.
    """
    if not tle or EarthSatellite is None or load is None:
        return _fallback_ground_track(
            predicted_lat or 0,
            predicted_lon or 0,
            uncertainty_minutes,
            samples,
        )

    try:
        satellite = EarthSatellite(tle[0], tle[1])
        timescale = load.timescale()
        start = epoch - timedelta(minutes=uncertainty_minutes)
        step = (uncertainty_minutes * 2) / max(samples - 1, 1)
        points: list[tuple[float, float]] = []
        for index in range(samples):
            instant = start + timedelta(minutes=step * index)
            time = timescale.from_datetime(instant)
            geocentric = satellite.at(time)
            points.append(_subpoint_from_state(tuple(geocentric.position.km)))
        return points
    except Exception:
        return _fallback_ground_track(
            predicted_lat or 0,
            predicted_lon or 0,
            uncertainty_minutes,
            samples,
        )


def great_circle_distance_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    lat1, lon1 = map(radians, a)
    lat2, lon2 = map(radians, b)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    hav = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 6371.0 * 2 * atan2(hav**0.5, (1 - hav) ** 0.5)
