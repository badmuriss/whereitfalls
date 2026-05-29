from fastapi import APIRouter, Depends, Query

from app.core.config import Settings, get_settings
from app.schemas.api import FeatureCollection, RiskResponse
from app.services.reentries import reentry_service

router = APIRouter(prefix="/v1/risk", tags=["risk"])


@router.get("", response_model=RiskResponse)
async def list_risk(
    region: str | None = None,
    min_score: float = Query(default=0, ge=0, le=1),
    settings: Settings = Depends(get_settings),
) -> RiskResponse:
    return await reentry_service.risk(settings, region=region, min_score=min_score)


@router.get("/heatmap", response_model=FeatureCollection)
async def risk_heatmap(settings: Settings = Depends(get_settings)) -> dict[str, object]:
    return await reentry_service.heatmap(settings)
