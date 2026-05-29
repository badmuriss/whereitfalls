from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.schemas.api import (
    AlertDispatchRequest,
    AlertDispatchResponse,
    AlertEmailTestRequest,
    AlertEmailTestResponse,
)
from app.services.alert_dispatch import dispatch_region_alerts
from app.services.alerts import send_alert_email

router = APIRouter(prefix="/v1/alerts", tags=["alerts"])


@router.post("/email/test", response_model=AlertEmailTestResponse)
async def test_email_alert(
    payload: AlertEmailTestRequest,
    settings: Settings = Depends(get_settings),
) -> AlertEmailTestResponse:
    if settings.resend_api_key:
        provider = "resend"
    elif settings.email_host:
        provider = "smtp"
    else:
        provider = "not_configured"
    subject = f"WhereItFalls alerta de risco - {payload.region}"
    text = (
        f"Regiao {payload.region} sob corredor de incerteza. Score operacional {payload.score:.2f}."
    )
    html = (
        "<strong>WhereItFalls</strong><br/>"
        f"Regiao {payload.region} sob corredor de incerteza.<br/>"
        f"Score operacional: {payload.score:.2f}."
    )

    if payload.dry_run:
        return AlertEmailTestResponse(
            provider=provider,
            sent=False,
            detail="Dry run: payload validated; no email was sent.",
        )

    result = await send_alert_email(settings, payload.to_email, subject, html, text)
    return AlertEmailTestResponse(
        provider=result.provider,  # type: ignore[arg-type]
        sent=result.sent,
        message_id=result.message_id,
        detail=result.detail,
    )


@router.post("/dispatch", response_model=AlertDispatchResponse)
async def dispatch_alerts(
    payload: AlertDispatchRequest,
    settings: Settings = Depends(get_settings),
) -> AlertDispatchResponse:
    result = await dispatch_region_alerts(
        settings,
        dry_run=payload.dry_run,
        min_score=payload.min_score,
    )
    return AlertDispatchResponse(**result.__dict__)
