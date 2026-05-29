from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.config import Settings, get_settings
from app.schemas.api import IngestSyncResponse, RiskRecomputeResponse
from app.services.ingest import SpaceTrackClient
from app.services.ingestion_sync import sync_spacetrack_ingest
from app.services.risk_recompute import recompute_stored_risk_corridors

router = APIRouter(prefix="/v1/ingest", tags=["ingest"])


class SpaceTrackSmokeResponse(BaseModel):
    authenticated: bool
    tip_count: int
    sample_norad_id: int | None = None
    sample_epoch: datetime | None = None


@router.post("/spacetrack/smoke", response_model=SpaceTrackSmokeResponse)
async def spacetrack_smoke(settings: Settings = Depends(get_settings)) -> SpaceTrackSmokeResponse:
    status = await SpaceTrackClient(settings).smoke_test()
    return SpaceTrackSmokeResponse(**status.__dict__)


@router.post("/spacetrack/sync", response_model=IngestSyncResponse)
async def spacetrack_sync(
    limit: int = 8,
    settings: Settings = Depends(get_settings),
) -> IngestSyncResponse:
    result = await sync_spacetrack_ingest(settings, limit=limit)
    return IngestSyncResponse(**result.__dict__)


@router.post("/risk/recompute", response_model=RiskRecomputeResponse)
def risk_recompute(
    limit: int = 25,
    settings: Settings = Depends(get_settings),
) -> RiskRecomputeResponse:
    result = recompute_stored_risk_corridors(settings, limit=limit)
    return RiskRecomputeResponse(**result.__dict__)
