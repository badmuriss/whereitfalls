from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.core.errors import AppError
from app.schemas.api import SubscriptionCreate, SubscriptionResponse
from app.services.repository import create_subscription

router = APIRouter(prefix="/v1/subscriptions", tags=["subscriptions"])


@router.post("", response_model=SubscriptionResponse, status_code=201)
def create_region_subscription(
    payload: SubscriptionCreate,
    settings: Settings = Depends(get_settings),
) -> SubscriptionResponse:
    if payload.channel == "email" and not payload.email:
        raise AppError("email_required", "Email subscriptions require an email address.")
    if payload.channel == "webhook" and not payload.webhook_id:
        raise AppError("webhook_required", "Webhook subscriptions require a webhook_id.")
    if payload.target.type == "region" and not payload.target.region:
        raise AppError("region_required", "Region targets require a region code.")
    subscription = create_subscription(
        settings,
        channel=payload.channel,
        region=payload.target.region or "BR",
        min_score=payload.min_score,
        email=payload.email,
        webhook_id=payload.webhook_id,
    )
    if subscription is None or subscription.id is None:
        raise AppError("subscription_store_unavailable", "Could not persist subscription.", 503)
    return SubscriptionResponse(
        id=f"sub_{subscription.id}",
        channel=subscription.channel,
        target=payload.target,
        min_score=subscription.min_score,
        status="active",
    )
