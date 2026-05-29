import json
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, select

from app.core.config import Settings
from app.core.database import get_engine
from app.models.domain import (
    AlertEvent,
    ObjectType,
    ReentryPrediction,
    RiskCorridor,
    SpaceObject,
    Subscription,
)
from app.services.ingest import ReentryCandidate, ReentrySource

_MEMORY_SUBSCRIPTIONS: list[Subscription] = []
_MEMORY_ALERT_EVENTS: list[AlertEvent] = []
_MEMORY_SUBSCRIPTION_ID = 1
_MEMORY_ALERT_EVENT_ID = 1


@dataclass(frozen=True)
class PersistenceResult:
    available: bool
    stored: int
    detail: str = ""


@dataclass(frozen=True)
class AlertEventResult:
    available: bool
    event: AlertEvent | None = None
    duplicate: bool = False
    detail: str = ""


def upsert_reentry_candidates(
    settings: Settings,
    candidates: list[ReentryCandidate],
) -> PersistenceResult:
    try:
        engine = get_engine(settings.database_url)
        with Session(engine) as session:
            stored = 0
            for candidate in candidates:
                _upsert_candidate(session, candidate)
                stored += 1
            session.commit()
    except SQLAlchemyError as exc:
        return PersistenceResult(available=False, stored=0, detail=str(exc))
    return PersistenceResult(available=True, stored=stored)


def list_stored_reentry_candidates(
    settings: Settings,
    limit: int = 25,
) -> list[ReentryCandidate]:
    try:
        engine = get_engine(settings.database_url)
        with Session(engine) as session:
            predictions = session.exec(
                select(ReentryPrediction)
                .order_by(ReentryPrediction.predicted_reentry_utc.desc())
                .limit(limit)
            ).all()
            candidates = []
            for prediction in predictions:
                space_object = session.exec(
                    select(SpaceObject).where(SpaceObject.norad_id == prediction.norad_id)
                ).first()
                candidates.append(_candidate_from_models(prediction, space_object))
            return candidates
    except SQLAlchemyError:
        return []


def upsert_risk_corridor(
    settings: Settings,
    prediction_id: str,
    corridor_geojson: dict[str, object],
    max_region_score: float,
) -> PersistenceResult:
    try:
        engine = get_engine(settings.database_url)
        with Session(engine) as session:
            corridor = session.exec(
                select(RiskCorridor).where(RiskCorridor.prediction_id == prediction_id)
            ).first()
            if corridor is None:
                corridor = RiskCorridor(
                    prediction_id=prediction_id,
                    corridor_geojson=json.dumps(corridor_geojson),
                    max_region_score=max_region_score,
                )
            else:
                corridor.corridor_geojson = json.dumps(corridor_geojson)
                corridor.max_region_score = max_region_score
            session.add(corridor)
            session.commit()
    except SQLAlchemyError as exc:
        return PersistenceResult(available=False, stored=0, detail=str(exc))
    return PersistenceResult(available=True, stored=1)


def count_risk_corridors(settings: Settings) -> int:
    try:
        engine = get_engine(settings.database_url)
        with Session(engine) as session:
            return len(session.exec(select(RiskCorridor)).all())
    except SQLAlchemyError:
        return 0


def create_subscription(
    settings: Settings,
    channel: str,
    region: str,
    min_score: float,
    email: str | None = None,
    webhook_id: str | None = None,
) -> Subscription | None:
    global _MEMORY_SUBSCRIPTION_ID
    try:
        engine = get_engine(settings.database_url)
        with Session(engine) as session:
            subscription = Subscription(
                channel=channel,
                region=region.upper(),
                min_score=min_score,
                email=email,
                webhook_id=webhook_id,
            )
            session.add(subscription)
            session.commit()
            session.refresh(subscription)
            return subscription
    except SQLAlchemyError:
        subscription = Subscription(
            id=_MEMORY_SUBSCRIPTION_ID,
            channel=channel,
            region=region.upper(),
            min_score=min_score,
            email=email,
            webhook_id=webhook_id,
        )
        _MEMORY_SUBSCRIPTION_ID += 1
        _MEMORY_SUBSCRIPTIONS.append(subscription)
        return subscription


def list_subscriptions(settings: Settings) -> list[Subscription]:
    try:
        engine = get_engine(settings.database_url)
        with Session(engine) as session:
            return list(session.exec(select(Subscription)).all())
    except SQLAlchemyError:
        return list(_MEMORY_SUBSCRIPTIONS)


def record_alert_event(
    settings: Settings,
    prediction_id: str,
    subscription_id: int,
    region: str,
    score: float,
    status: str,
    provider: str | None = None,
    message_id: str | None = None,
    detail: str = "",
    dry_run: bool = True,
) -> AlertEventResult:
    global _MEMORY_ALERT_EVENT_ID
    try:
        engine = get_engine(settings.database_url)
        with Session(engine) as session:
            existing = session.exec(
                select(AlertEvent).where(
                    AlertEvent.prediction_id == prediction_id,
                    AlertEvent.subscription_id == subscription_id,
                    AlertEvent.region == region.upper(),
                    AlertEvent.dry_run == dry_run,
                    AlertEvent.status == status,
                )
            ).first()
            if existing is not None:
                return AlertEventResult(available=True, event=existing, duplicate=True)
            event = AlertEvent(
                prediction_id=prediction_id,
                subscription_id=subscription_id,
                region=region.upper(),
                score=score,
                status=status,
                provider=provider,
                message_id=message_id,
                detail=detail,
                dry_run=dry_run,
                sent_at=datetime.now(UTC) if status == "sent" else None,
            )
            session.add(event)
            session.commit()
            session.refresh(event)
            return AlertEventResult(available=True, event=event)
    except SQLAlchemyError as exc:
        for existing in _MEMORY_ALERT_EVENTS:
            if (
                existing.prediction_id == prediction_id
                and existing.subscription_id == subscription_id
                and existing.region == region.upper()
                and existing.dry_run == dry_run
                and existing.status == status
            ):
                return AlertEventResult(
                    available=False,
                    event=existing,
                    duplicate=True,
                    detail=str(exc),
                )
        event = AlertEvent(
            id=_MEMORY_ALERT_EVENT_ID,
            prediction_id=prediction_id,
            subscription_id=subscription_id,
            region=region.upper(),
            score=score,
            status=status,
            provider=provider,
            message_id=message_id,
            detail=detail,
            dry_run=dry_run,
            sent_at=datetime.now(UTC) if status == "sent" else None,
        )
        _MEMORY_ALERT_EVENT_ID += 1
        _MEMORY_ALERT_EVENTS.append(event)
        return AlertEventResult(available=False, event=event, detail=str(exc))


def clear_memory_store() -> None:
    global _MEMORY_ALERT_EVENT_ID, _MEMORY_SUBSCRIPTION_ID
    _MEMORY_SUBSCRIPTIONS.clear()
    _MEMORY_ALERT_EVENTS.clear()
    _MEMORY_SUBSCRIPTION_ID = 1
    _MEMORY_ALERT_EVENT_ID = 1


def _upsert_candidate(session: Session, candidate: ReentryCandidate) -> None:
    space_object = session.exec(
        select(SpaceObject).where(SpaceObject.norad_id == candidate.norad_id)
    ).first()
    if space_object is None:
        space_object = SpaceObject(
            norad_id=candidate.norad_id,
            name=candidate.name,
            type=candidate.type,
            country=candidate.country,
        )
    else:
        space_object.name = candidate.name
        space_object.type = candidate.type
        space_object.country = candidate.country
    session.add(space_object)

    prediction = session.exec(
        select(ReentryPrediction).where(ReentryPrediction.prediction_id == candidate.prediction_id)
    ).first()
    tle_line1, tle_line2 = candidate.tle or (None, None)
    if prediction is None:
        prediction = ReentryPrediction(
            prediction_id=candidate.prediction_id,
            norad_id=candidate.norad_id,
            source=candidate.source.value,
            predicted_reentry_utc=candidate.predicted_reentry_utc,
            uncertainty_minutes=candidate.uncertainty_minutes,
            predicted_lat=candidate.predicted_lat,
            predicted_lon=candidate.predicted_lon,
            confidence=candidate.confidence,
            max_region_score=candidate.max_region_score,
            tle_line1=tle_line1,
            tle_line2=tle_line2,
        )
    else:
        prediction.source = candidate.source.value
        prediction.predicted_reentry_utc = candidate.predicted_reentry_utc
        prediction.uncertainty_minutes = candidate.uncertainty_minutes
        prediction.predicted_lat = candidate.predicted_lat
        prediction.predicted_lon = candidate.predicted_lon
        prediction.confidence = candidate.confidence
        prediction.max_region_score = candidate.max_region_score
        prediction.tle_line1 = tle_line1
        prediction.tle_line2 = tle_line2
    session.add(prediction)


def _candidate_from_models(
    prediction: ReentryPrediction,
    space_object: SpaceObject | None,
) -> ReentryCandidate:
    tle = None
    if prediction.tle_line1 and prediction.tle_line2:
        tle = (prediction.tle_line1, prediction.tle_line2)
    return ReentryCandidate(
        prediction_id=prediction.prediction_id,
        norad_id=prediction.norad_id,
        name=space_object.name if space_object else f"NORAD {prediction.norad_id}",
        type=space_object.type if space_object else ObjectType.payload,
        country=space_object.country if space_object else "UNK",
        predicted_reentry_utc=prediction.predicted_reentry_utc,
        uncertainty_minutes=prediction.uncertainty_minutes,
        predicted_lat=prediction.predicted_lat,
        predicted_lon=prediction.predicted_lon,
        confidence=prediction.confidence,
        max_region_score=prediction.max_region_score,
        tle=tle,
        source=ReentrySource(prediction.source),
    )
