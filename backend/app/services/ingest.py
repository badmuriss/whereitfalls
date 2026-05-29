from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

import httpx

from app.core.config import Settings
from app.core.errors import AppError
from app.models.domain import Confidence, ObjectType


class ReentrySource(StrEnum):
    spacetrack = "spacetrack"
    demo = "demo"


SPACETRACK_BASE = "https://www.space-track.org"


@dataclass(frozen=True)
class SpaceTrackStatus:
    authenticated: bool
    tip_count: int
    sample_norad_id: int | None = None
    sample_epoch: datetime | None = None


@dataclass(frozen=True)
class ReentryCandidate:
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
    tle: tuple[str, str] | None
    source: ReentrySource


class SpaceTrackClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def _require_credentials(self) -> tuple[str, str]:
        if not self.settings.spacetrack_user or not self.settings.spacetrack_pass:
            raise AppError(
                "spacetrack_not_configured",
                "SPACETRACK_USER and SPACETRACK_PASS are required.",
                status_code=503,
            )
        return self.settings.spacetrack_user, self.settings.spacetrack_pass

    async def login(self, client: httpx.AsyncClient) -> None:
        user, password = self._require_credentials()
        response = await client.post(
            f"{SPACETRACK_BASE}/ajaxauth/login",
            data={"identity": user, "password": password},
        )
        if response.status_code >= 400 or "Login Failed" in response.text:
            raise AppError(
                "spacetrack_auth_failed",
                "Space-Track rejected the configured credentials.",
                status_code=502,
            )

    async def fetch_recent_tips(self, limit: int = 5) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(
            base_url=SPACETRACK_BASE,
            timeout=30,
            follow_redirects=True,
        ) as client:
            await self.login(client)
            response = await client.get(
                "/basicspacedata/query/class/tip/orderby/MSG_EPOCH%20desc/format/json",
                params={"limit": str(limit)},
            )
        if response.status_code >= 400:
            raise AppError(
                "spacetrack_query_failed",
                f"Space-Track TIP query failed with HTTP {response.status_code}.",
                status_code=502,
            )
        payload = response.json()
        if not isinstance(payload, list):
            raise AppError(
                "spacetrack_unexpected_response",
                "Space-Track returned an unexpected TIP payload.",
                status_code=502,
            )
        return payload

    async def fetch_gp(self, norad_id: int, client: httpx.AsyncClient) -> dict[str, Any] | None:
        response = await client.get(
            f"/basicspacedata/query/class/gp/NORAD_CAT_ID/{norad_id}/format/json"
        )
        if response.status_code >= 400:
            return None
        payload = response.json()
        if not isinstance(payload, list) or not payload:
            return None
        first = payload[0]
        return first if isinstance(first, dict) else None

    async def fetch_reentry_candidates(self, limit: int = 6) -> list[ReentryCandidate]:
        async with httpx.AsyncClient(
            base_url=SPACETRACK_BASE,
            timeout=30,
            follow_redirects=True,
        ) as client:
            await self.login(client)
            response = await client.get(
                "/basicspacedata/query/class/tip/orderby/MSG_EPOCH%20desc/format/json",
                params={"limit": str(limit)},
            )
            if response.status_code >= 400:
                raise AppError(
                    "spacetrack_query_failed",
                    f"Space-Track TIP query failed with HTTP {response.status_code}.",
                    status_code=502,
                )
            tips = response.json()
            if not isinstance(tips, list):
                raise AppError(
                    "spacetrack_unexpected_response",
                    "Space-Track returned an unexpected TIP payload.",
                    status_code=502,
                )

            candidates: list[ReentryCandidate] = []
            for tip in tips:
                if not isinstance(tip, dict):
                    continue
                candidate = await self._candidate_from_tip(tip, client)
                if candidate is not None:
                    candidates.append(candidate)
            return candidates

    async def _candidate_from_tip(
        self,
        tip: dict[str, Any],
        client: httpx.AsyncClient,
    ) -> ReentryCandidate | None:
        norad_id = _parse_int(tip.get("NORAD_CAT_ID"))
        decay_epoch = _parse_spacetrack_datetime(tip.get("DECAY_EPOCH"))
        if norad_id is None or decay_epoch is None:
            return None

        gp = await self.fetch_gp(norad_id, client)
        uncertainty = max(30, _parse_int(tip.get("WINDOW")) or 1440)
        object_name = _string_or_none(gp.get("OBJECT_NAME") if gp else None)
        object_type = _object_type(gp.get("OBJECT_TYPE") if gp else None)
        country = _string_or_none(gp.get("COUNTRY_CODE") if gp else None) or "UNK"
        tle = _tle_from_gp(gp)
        lat = _parse_float(tip.get("LAT"))
        lon = _normalize_lon(_parse_float(tip.get("LON")))

        return ReentryCandidate(
            prediction_id=f"st-tip-{tip.get('ID') or norad_id}-{decay_epoch:%Y%m%dT%H%M%SZ}",
            norad_id=norad_id,
            name=object_name or f"NORAD {norad_id}",
            type=object_type,
            country=country,
            predicted_reentry_utc=decay_epoch,
            uncertainty_minutes=uncertainty,
            predicted_lat=lat,
            predicted_lon=lon,
            confidence=_confidence_from_window(uncertainty),
            max_region_score=_base_region_score(lat, lon, uncertainty),
            tle=tle,
            source=ReentrySource.spacetrack,
        )

    async def smoke_test(self) -> SpaceTrackStatus:
        tips = await self.fetch_recent_tips(limit=1)
        sample = tips[0] if tips else {}
        sample_norad = sample.get("NORAD_CAT_ID")
        sample_epoch = sample.get("MSG_EPOCH")
        return SpaceTrackStatus(
            authenticated=True,
            tip_count=len(tips),
            sample_norad_id=int(sample_norad) if sample_norad else None,
            sample_epoch=_parse_spacetrack_datetime(sample_epoch),
        )


def _parse_spacetrack_datetime(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    normalized = value.replace(" ", "T").replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def _parse_int(value: object) -> int | None:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return None


def _parse_float(value: object) -> float | None:
    try:
        parsed = float(str(value))
    except (TypeError, ValueError):
        return None
    return parsed


def _normalize_lon(value: float | None) -> float | None:
    if value is None:
        return None
    return round(((value + 180) % 360) - 180, 4)


def _string_or_none(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


def _object_type(value: object) -> ObjectType:
    normalized = str(value or "").lower()
    if "rocket" in normalized or "body" in normalized:
        return ObjectType.rocket_body
    if "debris" in normalized:
        return ObjectType.debris
    return ObjectType.payload


def _tle_from_gp(gp: dict[str, Any] | None) -> tuple[str, str] | None:
    if not gp:
        return None
    line1 = _string_or_none(gp.get("TLE_LINE1"))
    line2 = _string_or_none(gp.get("TLE_LINE2"))
    if not line1 or not line2:
        return None
    return line1, line2


def _confidence_from_window(uncertainty_minutes: int) -> Confidence:
    if uncertainty_minutes <= 180:
        return Confidence.high
    if uncertainty_minutes <= 720:
        return Confidence.medium
    return Confidence.low


def _base_region_score(lat: float | None, lon: float | None, uncertainty_minutes: int) -> float:
    if lat is None or lon is None:
        return 0.35
    brazil_centers = [(-15.8, -47.9), (-23.5, -46.6), (-22.9, -43.2), (-3.7, -38.5)]
    nearest_degrees = min(
        ((lat - b_lat) ** 2 + (lon - b_lon) ** 2) ** 0.5 for b_lat, b_lon in brazil_centers
    )
    proximity = max(0.0, 1 - nearest_degrees / 65)
    uncertainty_penalty = 0.75 if uncertainty_minutes > 1440 else 1.0
    return round(min(0.95, max(0.18, (0.25 + proximity * 0.75) * uncertainty_penalty)), 2)
