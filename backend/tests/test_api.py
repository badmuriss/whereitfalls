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


def test_webhook_subscription_contract() -> None:
    client = TestClient(create_app())
    response = client.post(
        "/v1/subscriptions",
        json={
            "channel": "webhook",
            "target": {"type": "region", "region": "DF"},
            "min_score": 0.1,
            "webhook_id": "wh_test",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["channel"] == "webhook"
    assert body["status"] == "active"
