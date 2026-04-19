import pytest
from flask_jwt_extended import create_access_token


def get_admin_token(app):
    with app.app_context():
        return create_access_token(identity="admin", additional_claims={"role": "admin"})


def get_user_token(app):
    with app.app_context():
        return create_access_token(identity="user", additional_claims={"role": "user"})

def test_dashboard_admin_access(client, app):
    token = get_admin_token(app)

    response = client.get(
        "/api/admin/dashboard",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.get_json()

    assert "pending_orders" in data
    assert "today_revenue" in data


def test_dashboard_non_admin(client, app):
    token = get_user_token(app)

    response = client.get(
        "/api/admin/dashboard",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403


def test_get_users_admin(client, app):
    token = get_admin_token(app)

    response = client.get(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_get_users_filter_role(client, app):
    token = get_admin_token(app)

    response = client.get(
        "/api/admin/users?role=packer",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

def test_get_packers(client, app):
    token = get_admin_token(app)

    response = client.get(
        "/api/admin/packers",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

def test_assign_packer_missing_fields(client, app):
    token = get_admin_token(app)

    response = client.post(
        "/api/admin/orders/assign-packer",
        json={},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400

def test_assign_packer_non_admin(client, app):
    token = get_user_token(app)

    response = client.post(
        "/api/admin/orders/assign-packer",
        json={"order_id": 1, "packer_id": 1},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403

def test_assign_packer_invalid_order(client, app):
    token = get_admin_token(app)

    response = client.post(
        "/api/admin/orders/assign-packer",
        json={"order_id": 999, "packer_id": 1},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code in [404, 400]

