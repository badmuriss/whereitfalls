from dataclasses import dataclass

from app.core.config import Settings
from app.services.orbit import propagate_ground_track
from app.services.repository import (
    list_stored_reentry_candidates,
    upsert_risk_corridor,
)
from app.services.risk import build_corridor_geojson


@dataclass(frozen=True)
class RiskRecomputeResult:
    candidates: int
    stored_corridors: int
    database_available: bool
    detail: str = ""


def recompute_stored_risk_corridors(settings: Settings, limit: int = 25) -> RiskRecomputeResult:
    candidates = list_stored_reentry_candidates(settings, limit=limit)
    stored = 0
    database_available = True
    detail = ""
    for candidate in candidates:
        track = propagate_ground_track(
            candidate.tle,
            candidate.predicted_reentry_utc,
            candidate.uncertainty_minutes,
            candidate.predicted_lat,
            candidate.predicted_lon,
        )
        corridor = build_corridor_geojson(track, candidate.uncertainty_minutes)
        result = upsert_risk_corridor(
            settings,
            candidate.prediction_id,
            corridor,
            candidate.max_region_score,
        )
        if not result.available:
            database_available = False
            detail = result.detail
            break
        stored += result.stored
    return RiskRecomputeResult(
        candidates=len(candidates),
        stored_corridors=stored,
        database_available=database_available,
        detail=detail,
    )
