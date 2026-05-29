from dataclasses import dataclass

from app.core.config import Settings
from app.schemas.api import AlertDispatchItem
from app.services.alerts import send_alert_email
from app.services.reentries import reentry_service
from app.services.repository import list_subscriptions, record_alert_event


@dataclass(frozen=True)
class AlertDispatchResult:
    evaluated: int
    matched: int
    sent: int
    events: list[AlertDispatchItem]


async def dispatch_region_alerts(
    settings: Settings,
    dry_run: bool = True,
    min_score: float = 0,
) -> AlertDispatchResult:
    subscriptions = list_subscriptions(settings)
    risk = await reentry_service.risk(settings, min_score=min_score)
    events: list[AlertDispatchItem] = []
    sent = 0

    for item in risk.items:
        for subscription in subscriptions:
            if subscription.id is None:
                continue
            if subscription.channel != "email":
                continue
            if subscription.region.upper() != item.region.upper():
                continue
            if item.score < subscription.min_score:
                continue
            if not subscription.email:
                continue

            status = "dry_run"
            if settings.resend_api_key:
                provider = "resend"
            elif settings.email_host:
                provider = "smtp"
            else:
                provider = None
            message_id = None
            detail = "Dry run: no email sent."

            if not dry_run:
                email = await send_alert_email(
                    settings,
                    subscription.email,
                    f"WhereItFalls alerta de risco - {item.region}",
                    _alert_html(item.region, item.score, item.prediction_id, item.exposed_assets),
                    _alert_text(item.region, item.score, item.prediction_id, item.exposed_assets),
                )
                status = "sent" if email.sent else "failed"
                provider = email.provider
                message_id = email.message_id
                detail = email.detail
                if email.sent:
                    sent += 1

            stored = record_alert_event(
                settings,
                prediction_id=item.prediction_id,
                subscription_id=subscription.id,
                region=item.region,
                score=item.score,
                status=status,
                provider=provider,
                message_id=message_id,
                detail=detail,
                dry_run=dry_run,
            )
            if stored.duplicate:
                status = "duplicate"
                detail = "Matching alert event already exists."

            events.append(
                AlertDispatchItem(
                    subscription_id=f"sub_{subscription.id}",
                    prediction_id=item.prediction_id,
                    region=item.region,
                    score=item.score,
                    status=status,
                    provider=provider,
                    message_id=message_id,
                    detail=detail,
                )
            )

    return AlertDispatchResult(
        evaluated=len(risk.items),
        matched=len(events),
        sent=sent,
        events=events,
    )


def _alert_text(region: str, score: float, prediction_id: str, assets: list[str]) -> str:
    asset_text = ", ".join(assets) if assets else "sem ativos nomeados"
    return (
        f"WhereItFalls alerta: regiao {region} sob corredor de risco. "
        f"Score {score:.2f}. Prediction {prediction_id}. Ativos: {asset_text}."
    )


def _alert_html(region: str, score: float, prediction_id: str, assets: list[str]) -> str:
    asset_text = ", ".join(assets) if assets else "sem ativos nomeados"
    return (
        "<strong>WhereItFalls alerta</strong><br/>"
        f"Regiao: {region}<br/>"
        f"Score: {score:.2f}<br/>"
        f"Prediction: {prediction_id}<br/>"
        f"Ativos: {asset_text}"
    )
