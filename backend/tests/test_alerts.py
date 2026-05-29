import pytest

from app.core.config import Settings
from app.services.alerts import send_resend_email


class FakeResponse:
    status_code = 200
    text = '{"id":"email_test"}'

    def json(self) -> dict[str, str]:
        return {"id": "email_test"}


class FakeAsyncClient:
    def __init__(self, *args: object, **kwargs: object) -> None:
        self.request: dict[str, object] | None = None

    async def __aenter__(self) -> "FakeAsyncClient":
        return self

    async def __aexit__(self, *args: object) -> None:
        return None

    async def post(self, url: str, **kwargs: object) -> FakeResponse:
        self.request = {"url": url, **kwargs}
        assert url == "https://api.resend.com/emails"
        headers = kwargs["headers"]
        assert isinstance(headers, dict)
        assert headers["Authorization"] == "Bearer re_test"
        json_payload = kwargs["json"]
        assert isinstance(json_payload, dict)
        assert json_payload["to"] == ["ops@example.com"]
        return FakeResponse()


@pytest.mark.asyncio
async def test_resend_email_posts_to_resend(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.services.alerts.httpx.AsyncClient", FakeAsyncClient)
    settings = Settings(resend_api_key="re_test", email_from="WhereItFalls <alerts@example.com>")

    result = await send_resend_email(
        settings,
        "ops@example.com",
        "Risk alert",
        "<p>risk</p>",
        "risk",
    )

    assert result.provider == "resend"
    assert result.sent is True
    assert result.message_id == "email_test"
