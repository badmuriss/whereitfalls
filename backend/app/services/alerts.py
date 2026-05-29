import hmac
import json
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from hashlib import sha256

import httpx

from app.core.config import Settings


def sign_webhook_payload(payload: dict[str, object], secret: str) -> str:
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    return hmac.new(secret.encode(), body, sha256).hexdigest()


async def send_webhook(url: str, payload: dict[str, object], secret: str) -> httpx.Response:
    signature = sign_webhook_payload(payload, secret)
    async with httpx.AsyncClient(timeout=10) as client:
        return await client.post(url, json=payload, headers={"X-WIF-Signature": signature})


@dataclass(frozen=True)
class EmailResult:
    provider: str
    sent: bool
    message_id: str | None = None
    detail: str = ""


async def send_resend_email(
    settings: Settings,
    to_email: str,
    subject: str,
    html: str,
    text: str,
) -> EmailResult:
    if not settings.resend_api_key:
        return EmailResult(
            provider="not_configured",
            sent=False,
            detail="RESEND_API_KEY is not set.",
        )

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {settings.resend_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": settings.email_from,
                "to": [to_email],
                "subject": subject,
                "html": html,
                "text": text,
            },
        )

    if response.status_code >= 400:
        return EmailResult(
            provider="resend",
            sent=False,
            detail=f"Resend API returned HTTP {response.status_code}: {response.text}",
        )

    payload = response.json()
    return EmailResult(
        provider="resend",
        sent=True,
        message_id=payload.get("id"),
        detail="Email accepted by Resend.",
    )


def send_smtp_email(settings: Settings, to_email: str, subject: str, body: str) -> EmailResult:
    if not settings.email_host:
        return EmailResult(provider="not_configured", sent=False, detail="EMAIL_HOST is not set.")
    message = EmailMessage()
    message["From"] = settings.email_from
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)
    with smtplib.SMTP(settings.email_host, settings.email_port, timeout=10) as smtp:
        smtp.starttls()
        if settings.email_user and settings.email_pass:
            smtp.login(settings.email_user, settings.email_pass)
        smtp.send_message(message)
    return EmailResult(provider="smtp", sent=True, detail="Email accepted by SMTP server.")


async def send_alert_email(
    settings: Settings,
    to_email: str,
    subject: str,
    html: str,
    text: str,
) -> EmailResult:
    if settings.resend_api_key:
        return await send_resend_email(settings, to_email, subject, html, text)
    return send_smtp_email(settings, to_email, subject, text)
