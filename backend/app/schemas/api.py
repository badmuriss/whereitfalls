from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.models.domain import Confidence, ObjectType


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str
    environment: str


class GeoJSONGeometry(BaseModel):
    type: str
    coordinates: object


class GeoJSONFeature(BaseModel):
    type: Literal["Feature"] = "Feature"
    geometry: GeoJSONGeometry
    properties: dict[str, object] = Field(default_factory=dict)


class FeatureCollection(BaseModel):
    type: Literal["FeatureCollection"] = "FeatureCollection"
    features: list[GeoJSONFeature]


class ReentrySummary(BaseModel):
    prediction_id: str
    norad_id: int
    name: str
    type: ObjectType
    country: str
    predicted_reentry_utc: datetime
    uncertainty_minutes: int
    predicted_lat: float | None
    predicted_lon: float | None
    confidence: Confidence
    max_region_score: float


class ReentryListResponse(BaseModel):
    items: list[ReentrySummary]
    total: int


class ReentryDetail(ReentrySummary):
    ground_track: list[tuple[float, float]]
    corridor_geojson: FeatureCollection


class RiskRegion(BaseModel):
    region: str
    label: str | None = None
    scope: str | None = None
    lat: float | None = None
    lon: float | None = None
    score: float = Field(ge=0, le=1)
    prediction_id: str
    norad_id: int
    window_utc: tuple[datetime, datetime]
    exposed_assets: list[str]


class RiskResponse(BaseModel):
    items: list[RiskRegion]
    total: int


class SubscriptionTarget(BaseModel):
    type: Literal["region", "bbox"]
    region: str | None = None
    bbox: tuple[float, float, float, float] | None = None


class SubscriptionCreate(BaseModel):
    channel: Literal["webhook"] = "webhook"
    target: SubscriptionTarget
    min_score: float = Field(ge=0, le=1)
    webhook_id: str | None = None


class SubscriptionResponse(BaseModel):
    id: str
    channel: str
    target: SubscriptionTarget
    min_score: float
    status: Literal["active"]


class IngestSyncResponse(BaseModel):
    source: str
    fetched: int
    stored: int
    database_available: bool
    detail: str = ""


class RiskRecomputeResponse(BaseModel):
    candidates: int
    stored_corridors: int
    database_available: bool
    detail: str = ""
