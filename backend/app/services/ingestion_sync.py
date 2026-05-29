from dataclasses import dataclass

from app.core.config import Settings
from app.services.ingest import SpaceTrackClient
from app.services.repository import upsert_reentry_candidates


@dataclass(frozen=True)
class IngestSyncResult:
    source: str
    fetched: int
    stored: int
    database_available: bool
    detail: str = ""


async def sync_spacetrack_ingest(settings: Settings, limit: int = 8) -> IngestSyncResult:
    candidates = await SpaceTrackClient(settings).fetch_reentry_candidates(limit=limit)
    persistence = upsert_reentry_candidates(settings, candidates)
    return IngestSyncResult(
        source="spacetrack",
        fetched=len(candidates),
        stored=persistence.stored,
        database_available=persistence.available,
        detail=persistence.detail,
    )
