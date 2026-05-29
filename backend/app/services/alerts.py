import hmac
import json
from hashlib import sha256

import httpx


def sign_webhook_payload(payload: dict[str, object], secret: str) -> str:
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    return hmac.new(secret.encode(), body, sha256).hexdigest()


async def send_webhook(url: str, payload: dict[str, object], secret: str) -> httpx.Response:
    signature = sign_webhook_payload(payload, secret)
    async with httpx.AsyncClient(timeout=10) as client:
        return await client.post(url, json=payload, headers={"X-WIF-Signature": signature})
