import pytest
from flask_jwt_extended import create_access_token


# 🔐 Tokens
def get_admin_token(app):
    with app.app_context():
        return create_access_token(
            identity="admin@test.com",
            additional_claims={"role": "admin"}
        )


def get_user_token(app):
    with app.app_context():
        return create_access_token(
            identity="user@test.com",
            additional_claims={"role": "user"}
        )


# 🔹 1. SALES SUMMARY TESTS

def test_sales_summary_admin(client, app):
    token = get_admin_token(app)

    response = client.get(
        "/api/analytics/sales",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.get_json()

    assert "last_7_days" in data
    assert len(data["last_7_days"]) == 7
    assert "total_revenue" in data
    assert "total_quantity_sold" in data


def test_sales_summary_non_admin(client, app):
    token = get_user_token(app)

    response = client.get(
        "/api/analytics/sales",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403


def test_sales_summary_values(client, app):
    """Works even if DB has data"""
    token = get_admin_token(app)

    response = client.get(
        "/api/analytics/sales",
        headers={"Authorization": f"Bearer {token}"}
    )

    data = response.get_json()

    assert response.status_code == 200
    assert isinstance(data["total_revenue"], (int, float))
    assert isinstance(data["total_quantity_sold"], int)


# 🔹 2. TOP PRODUCTS TESTS

def test_top_products_default(client, app):
    token = get_admin_token(app)

    response = client.get(
        "/api/analytics/top-products",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.get_json()

    assert isinstance(data, list)


def test_top_products_limit(client, app):
    token = get_admin_token(app)

    response = client.get(
        "/api/analytics/top-products?limit=3",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.get_json()

    assert len(data) <= 3


def test_top_products_non_admin(client, app):
    token = get_user_token(app)

    response = client.get(
        "/api/analytics/top-products",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403

def test_top_products_limit_numeric(client, app):
    token = get_admin_token(app)

    response = client.get(
        "/api/analytics/top-products?limit=3",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert len(data) <= 3

# # 🔹 3. FORECAST TESTS

# def test_forecast_admin(client, app):
#     token = get_admin_token(app)

#     response = client.get(
#         "/api/analytics/forecast",
#         headers={"Authorization": f"Bearer {token}"}
#     )

#     assert response.status_code == 200
#     data = response.get_json()

#     assert isinstance(data, list)


# def test_forecast_non_admin(client, app):
#     token = get_user_token(app)

#     response = client.get(
#         "/api/analytics/forecast",
#         headers={"Authorization": f"Bearer {token}"}
#     )

#     assert response.status_code == 403


# def test_forecast_structure(client, app):
#     """Check structure instead of empty assumption"""
#     token = get_admin_token(app)

#     response = client.get(
#         "/api/analytics/forecast",
#         headers={"Authorization": f"Bearer {token}"}
#     )

#     data = response.get_json()

#     assert response.status_code == 200

#     if len(data) > 0:
#         item = data[0]
#         assert "forecast_date" in item
#         assert "product_id" in item
#         assert "predicted_demand" in item