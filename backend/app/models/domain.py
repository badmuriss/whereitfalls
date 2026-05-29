from datetime import UTC, datetime
from enum import StrEnum

from sqlmodel import Field, SQLModel


class ObjectType(StrEnum):
    payload = "payload"
    rocket_body = "rocket_body"
    debris = "debris"


class Confidence(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"


class SpaceObject(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    norad_id: int = Field(index=True, unique=True)
    name: str
    type: ObjectType
    country: str
    estimated_mass_kg: float | None = None


class ReentryPrediction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    prediction_id: str = Field(index=True, unique=True)
    norad_id: int = Field(index=True)
    source: str
    predicted_reentry_utc: datetime
    uncertainty_minutes: int
    predicted_lat: float | None = None
    predicted_lon: float | None = None
    orbit_number: int | None = None
    confidence: Confidence = Confidence.medium
    max_region_score: float = 0
    tle_line1: str | None = None
    tle_line2: str | None = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class RiskCorridor(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    prediction_id: str = Field(index=True)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    corridor_geojson: str
    max_region_score: float


class Subscription(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    channel: str
    region: str
    min_score: float
    email: str | None = None
    webhook_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AlertEvent(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    prediction_id: str = Field(index=True)
    subscription_id: int = Field(index=True)
    region: str = Field(index=True)
    score: float
    status: str
    provider: str | None = None
    message_id: str | None = None
    detail: str = ""
    dry_run: bool = True
    sent_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
