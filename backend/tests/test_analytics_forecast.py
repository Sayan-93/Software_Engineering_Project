from datetime import date

from models import db
from models.models import StockForecast


def test_forecast_requires_admin(client, auth_headers, users):
    response = client.get(
        "/api/analytics/forecast",
        headers=auth_headers(users["customer"]),
    )

    assert response.status_code == 403


def test_forecast_returns_saved_rows(client, auth_headers, users, sample_product, cleanup):
    forecast = cleanup(
        StockForecast(product_id=sample_product.id, predicted_demand=12, forecast_date=date(2030, 1, 1))
    )
    db.session.add(forecast)
    db.session.commit()

    response = client.get(
        "/api/analytics/forecast",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200
    assert any(item["product_id"] == sample_product.id for item in response.get_json())
