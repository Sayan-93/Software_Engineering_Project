from models.models import Inventory


def test_get_inventory_admin(client, auth_headers, users):
    response = client.get(
        "/api/inventory",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_get_inventory_non_admin_forbidden(client, auth_headers, users):
    response = client.get(
        "/api/inventory",
        headers=auth_headers(users["customer"]),
    )

    assert response.status_code == 403


def test_update_inventory(client, auth_headers, users, app_ctx):
    item = Inventory.query.first()

    response = client.put(
        f"/api/inventory/{item.id}",
        json={"stock_quantity": 77, "reorder_level": 11},
        headers=auth_headers(users["admin"]),
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data["inventory"]["stock_quantity"] == 77
    assert data["inventory"]["reorder_level"] == 11


def test_low_stock_alerts(client, auth_headers, users):
    response = client.get(
        "/api/inventory/low-stock",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200
    assert any(item["product_name"] == "Mango" for item in response.get_json())
