from datetime import datetime

from fastapi import APIRouter, Depends, Query

from app.core.config import Settings, get_settings
from app.core.errors import AppError
from app.schemas.api import ReentryDetail, ReentryListResponse
from app.services.reentries import reentry_service

router = APIRouter(prefix="/v1/reentries", tags=["reentries"])


@router.get("", response_model=ReentryListResponse)
async def list_reentries(
    date_from: datetime | None = Query(default=None, alias="from"),
    date_to: datetime | None = Query(default=None, alias="to"),
    min_confidence: str | None = None,
    limit: int = Query(default=25, ge=1, le=100),
    settings: Settings = Depends(get_settings),
) -> ReentryListResponse:
    return await reentry_service.list_reentries(settings, date_from, date_to, min_confidence, limit)


@router.get("/{norad_id}", response_model=ReentryDetail)
async def get_reentry(
    norad_id: int,
    settings: Settings = Depends(get_settings),
) -> ReentryDetail:
    detail = await reentry_service.get_detail(settings, norad_id)
    if detail is None:
        raise AppError("not_found", "Reentry prediction not found.", status_code=404)
    return detail
