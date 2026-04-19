from models.models import StockForecast


def test_get_recommendations(client, monkeypatch, sample_product):
    def fake_recommendations(product_id):
        return [{"product_id": product_id, "recommended_product_id": 2, "score": 3.0}]

    monkeypatch.setattr(
        "ai.recommendations.get_recommendations_for_product",
        fake_recommendations,
    )

    response = client.get(f"/api/products/{sample_product.id}/recommendations")

    assert response.status_code == 200
    assert response.get_json()[0]["product_id"] == sample_product.id


def test_rebuild_recommendations_requires_admin(client, auth_headers, users):
    response = client.post(
        "/api/ai/rebuild-recommendations",
        headers=auth_headers(users["customer"]),
    )

    assert response.status_code == 403


def test_rebuild_recommendations_calls_builder(client, auth_headers, users, monkeypatch):
    called = {"value": False}

    def fake_build():
        called["value"] = True

    monkeypatch.setattr("ai.recommendations.build_recommendations", fake_build)

    response = client.post(
        "/api/ai/rebuild-recommendations",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200
    assert called["value"] is True


def test_run_forecast_calls_forecast_function(client, auth_headers, users, monkeypatch):
    called = {"value": False}

    def fake_forecast():
        called["value"] = True

    monkeypatch.setattr("ai.forecasting.forecast_stock", fake_forecast)

    response = client.post(
        "/api/ai/run-forecast",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200
    assert called["value"] is True


def test_chatbot_requires_message(client):
    response = client.post("/api/chatbot", json={})

    assert response.status_code == 400


def test_chatbot_passes_user_id_when_authenticated(
    client,
    auth_headers,
    users,
    monkeypatch,
):
    captured = {}

    def fake_chatbot(message, user_id):
        captured["message"] = message
        captured["user_id"] = user_id
        return "stubbed response"

    monkeypatch.setattr("ai.chatbot.get_chatbot_response", fake_chatbot)

    response = client.post(
        "/api/chatbot",
        json={"message": "hello"},
        headers=auth_headers(users["customer"]),
    )

    assert response.status_code == 200
    assert response.get_json()["response"] == "stubbed response"
    assert captured["message"] == "hello"
    assert captured["user_id"] == users["customer"].id
