from fastapi.testclient import TestClient

from app.main import create_app


def test_health_endpoint() -> None:
    client = TestClient(create_app())
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_reentries_contract() -> None:
    client = TestClient(create_app())
    response = client.get("/v1/reentries")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert {"norad_id", "predicted_reentry_utc", "max_region_score"} <= set(body["items"][0])


def test_risk_heatmap_contract() -> None:
    client = TestClient(create_app())
    response = client.get("/v1/risk/heatmap")

    assert response.status_code == 200
    assert response.json()["type"] == "FeatureCollection"


def test_email_alert_dry_run_contract() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/v1/alerts/email/test",
        json={"to_email": "ops@example.com", "region": "DF", "score": 0.72},
    )

    assert response.status_code == 200
    assert response.json()["sent"] is False


def test_dispatch_alerts_contract() -> None:
    client = TestClient(create_app())
    subscription = client.post(
        "/v1/subscriptions",
        json={
            "channel": "email",
            "target": {"type": "region", "region": "DF"},
            "min_score": 0.1,
            "email": "ops@example.com",
        },
    )
    response = client.post(
        "/v1/alerts/dispatch",
        json={"dry_run": True, "min_score": 0.1},
    )

    assert subscription.status_code == 201
    assert response.status_code == 200
    assert {"evaluated", "matched", "sent", "events"} <= set(response.json())
