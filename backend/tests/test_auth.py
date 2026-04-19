from models.models import User


def test_register_success(client, app_ctx, unique_email):
    response = client.post(
        "/api/register",
        json={
            "name": "Pytest User",
            "email": unique_email,
            "password": "secret123",
            "role": "customer",
            "phone": "9999999999",
            "address": "Test Street",
            "flat_unit_number": "Flat 4A",
        },
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["user"]["email"] == unique_email
    assert data["user"]["flat_unit_number"] == "Flat 4A"

    user = User.query.filter_by(email=unique_email).first()
    assert user is not None
    assert user.flat_unit_number == "Flat 4A"


def test_register_rejects_duplicate_email(client):
    response = client.post(
        "/api/register",
        json={
            "name": "Duplicate User",
            "email": "rahul@example.com",
            "password": "secret123",
        },
    )

    assert response.status_code == 409


def test_register_requires_core_fields(client):
    response = client.post("/api/register", json={"email": "missing@example.com"})

    assert response.status_code == 400


def test_register_customer_requires_address_fields(client, unique_email):
    """Customer registrations must supply phone, address and flat_unit_number."""
    response = client.post(
        "/api/register",
        json={
            "name": "Incomplete Customer",
            "email": unique_email,
            "password": "secret123",
            "role": "customer",
            # Missing phone, address, flat_unit_number
        },
    )

    assert response.status_code == 400
    error_msg = response.get_json()["error"]
    assert "phone" in error_msg
    assert "address" in error_msg
    assert "flat_unit_number" in error_msg


def test_register_customer_requires_flat_unit_number(client, unique_email):
    """flat_unit_number alone being absent should still fail."""
    response = client.post(
        "/api/register",
        json={
            "name": "Partial Customer",
            "email": unique_email,
            "password": "secret123",
            "role": "customer",
            "phone": "9999999999",
            "address": "Some Street",
            # flat_unit_number missing
        },
    )

    assert response.status_code == 400
    assert "flat_unit_number" in response.get_json()["error"]


def test_register_non_customer_does_not_require_address_fields(client, unique_email):
    """Staff roles (packer, delivery, admin) don't need address fields."""
    response = client.post(
        "/api/register",
        json={
            "name": "Staff Member",
            "email": unique_email,
            "password": "secret123",
            "role": "packer",
        },
    )

    assert response.status_code == 201


def test_login_success(client):
    response = client.post(
        "/api/login",
        json={"email": "admin@freshmart.com", "password": "admin123"},
    )

    data = response.get_json()

    assert response.status_code == 200
    assert "token" in data
    assert data["role"] == "admin"


def test_login_rejects_invalid_password(client):
    response = client.post(
        "/api/login",
        json={"email": "admin@freshmart.com", "password": "wrong-password"},
    )

    assert response.status_code == 401
