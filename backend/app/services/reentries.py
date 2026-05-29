import asyncio
import logging
from datetime import UTC, datetime, timedelta

from app.core.config import Settings
from app.schemas.api import (
    ReentryDetail,
    ReentryListResponse,
    ReentrySummary,
    RiskRegion,
    RiskResponse,
)
from app.services.ingest import ReentryCandidate, ReentrySource, SpaceTrackClient
from app.services.orbit import propagate_ground_track
from app.services.repository import (
    list_stored_reentry_candidates,
    upsert_reentry_candidates,
    upsert_risk_corridor,
)
from app.services.risk import build_corridor_geojson, heatmap_features, score_regions
from app.services.sample_data import DEMO_REENTRIES, utc_window

logger = logging.getLogger(__name__)


class ReentryService:
    def __init__(self) -> None:
        self._live_cache: tuple[datetime, list[ReentryCandidate]] | None = None
        self._live_cache_ttl = timedelta(minutes=10)
        self._live_fetch_lock = asyncio.Lock()

    async def list_reentries(
        self,
        settings: Settings,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        min_confidence: str | None = None,
        limit: int = 25,
    ) -> ReentryListResponse:
        rows = await self._rows(settings, limit=limit)
        items = []
        for row in rows:
            if date_from and row.predicted_reentry_utc < date_from:
                continue
            if date_to and row.predicted_reentry_utc > date_to:
                continue
            if min_confidence and row.confidence != min_confidence:
                continue
            items.append(self._summary_from_candidate(row))
        return ReentryListResponse(items=items[:limit], total=len(items))

    async def get_detail(self, settings: Settings, norad_id: int) -> ReentryDetail | None:
        rows = await self._rows(settings, limit=12)
        row = next((item for item in rows if item.norad_id == norad_id), None)
        if row is None:
            return None
        track = propagate_ground_track(
            row.tle,
            row.predicted_reentry_utc,
            row.uncertainty_minutes,
            row.predicted_lat,
            row.predicted_lon,
        )
        corridor = build_corridor_geojson(track, row.uncertainty_minutes)
        upsert_risk_corridor(settings, row.prediction_id, corridor, row.max_region_score)
        return ReentryDetail(
            **self._summary_from_candidate(row).model_dump(),
            ground_track=track,
            corridor_geojson=corridor,
        )

    async def risk(
        self,
        settings: Settings,
        region: str | None = None,
        min_score: float = 0,
    ) -> RiskResponse:
        items: list[RiskRegion] = []
        rows = await self._rows(settings, limit=8)
        for row in rows:
            track = propagate_ground_track(
                row.tle,
                row.predicted_reentry_utc,
                row.uncertainty_minutes,
                row.predicted_lat,
                row.predicted_lon,
            )
            scores = score_regions(
                track,
                row.prediction_id,
                row.norad_id,
                row.max_region_score,
            )
            start, end = utc_window(row.predicted_reentry_utc, row.uncertainty_minutes)
            for score in scores:
                if region and score["region"] != region.upper():
                    continue
                if score["score"] < min_score:
                    continue
                items.append(RiskRegion(**score, window_utc=(start, end)))
        return RiskResponse(items=items, total=len(items))

    async def heatmap(self, settings: Settings) -> dict[str, object]:
        risk = await self.risk(settings, min_score=0.1)
        return heatmap_features(item.model_dump() for item in risk.items)

    async def _rows(self, settings: Settings, limit: int) -> list[ReentryCandidate]:
        stored_rows = list_stored_reentry_candidates(settings, limit=limit)
        if stored_rows:
            return stored_rows

        if settings.app_env != "test" and settings.spacetrack_user and settings.spacetrack_pass:
            try:
                rows = await self._live_rows(settings, limit)
                if rows:
                    return rows
            except Exception as exc:
                logger.warning("spacetrack_live_fallback", extra={"error": str(exc)})
        return self._demo_rows()

    async def _live_rows(self, settings: Settings, limit: int) -> list[ReentryCandidate]:
        now = datetime.now(UTC)
        if self._live_cache:
            fetched_at, rows = self._live_cache
            if now - fetched_at < self._live_cache_ttl and rows:
                return rows[:limit]

        async with self._live_fetch_lock:
            now = datetime.now(UTC)
            if self._live_cache:
                fetched_at, rows = self._live_cache
                if now - fetched_at < self._live_cache_ttl and rows:
                    return rows[:limit]

            rows = await SpaceTrackClient(settings).fetch_reentry_candidates(limit=max(limit, 8))
            future_rows = [row for row in rows if row.predicted_reentry_utc >= now]
            usable_rows = future_rows or rows
            upsert_reentry_candidates(settings, usable_rows)
            self._live_cache = (now, usable_rows)
            return usable_rows[:limit]

    def _demo_rows(self) -> list[ReentryCandidate]:
        return [
            ReentryCandidate(
                prediction_id=row["prediction_id"],
                norad_id=row["norad_id"],
                name=row["name"],
                type=row["type"],
                country=row["country"],
                predicted_reentry_utc=row["predicted_reentry_utc"],
                uncertainty_minutes=row["uncertainty_minutes"],
                predicted_lat=row["predicted_lat"],
                predicted_lon=row["predicted_lon"],
                confidence=row["confidence"],
                max_region_score=row["max_region_score"],
                tle=row["tle"],
                source=ReentrySource.demo,
            )
            for row in DEMO_REENTRIES
        ]

    def _summary_from_candidate(self, row: ReentryCandidate) -> ReentrySummary:
        return ReentrySummary(
            prediction_id=row.prediction_id,
            norad_id=row.norad_id,
            name=row.name,
            type=row.type,
            country=row.country,
            predicted_reentry_utc=row.predicted_reentry_utc,
            uncertainty_minutes=row.uncertainty_minutes,
            predicted_lat=row.predicted_lat,
            predicted_lon=row.predicted_lon,
            confidence=row.confidence,
            max_region_score=row.max_region_score,
        )


reentry_service = ReentryService()
