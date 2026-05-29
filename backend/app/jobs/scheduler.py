import asyncio
import logging

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import Settings
from app.services.alert_dispatch import dispatch_region_alerts
from app.services.ingestion_sync import sync_spacetrack_ingest
from app.services.risk_recompute import recompute_stored_risk_corridors

logger = logging.getLogger(__name__)


def pull_predictions(settings: Settings) -> None:
    logger.info("pull_predictions_started")
    if not settings.spacetrack_user or not settings.spacetrack_pass:
        logger.info("pull_predictions_skipped", extra={"reason": "spacetrack_not_configured"})
        return
    result = asyncio.run(sync_spacetrack_ingest(settings))
    logger.info(
        "pull_predictions_completed",
        extra={
            "source": result.source,
            "fetched": result.fetched,
            "stored": result.stored,
            "database_available": result.database_available,
        },
    )


def recompute_risk(settings: Settings) -> None:
    result = recompute_stored_risk_corridors(settings)
    logger.info(
        "recompute_risk_completed",
        extra={
            "candidates": result.candidates,
            "stored_corridors": result.stored_corridors,
            "database_available": result.database_available,
        },
    )


def dispatch_alerts(settings: Settings) -> None:
    result = asyncio.run(dispatch_region_alerts(settings, dry_run=False))
    logger.info(
        "dispatch_alerts_completed",
        extra={"matched": result.matched, "sent": result.sent},
    )


def build_scheduler(settings: Settings) -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(
        pull_predictions,
        "interval",
        hours=settings.ingest_interval_hours,
        id="pull_predictions",
        args=[settings],
    )
    scheduler.add_job(
        recompute_risk,
        "interval",
        hours=settings.ingest_interval_hours,
        id="recompute_risk",
        args=[settings],
    )
    scheduler.add_job(
        dispatch_alerts,
        "interval",
        minutes=30,
        id="dispatch_alerts",
        args=[settings],
    )
    return scheduler
