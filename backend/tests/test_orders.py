from models import db
from models.models import Cart, CartItem, Inventory, Order, Payment


def test_get_orders_for_customer_returns_only_their_orders(
    client,
    auth_headers,
    users,
    create_order,
    sample_product,
):
    customer_order = create_order(users["customer"], sample_product, status="pending")
    create_order(users["customer_two"], sample_product, status="pending")

    response = client.get("/api/orders", headers=auth_headers(users["customer"]))

    order_ids = {order["id"] for order in response.get_json()}

    assert response.status_code == 200
    assert customer_order.id in order_ids


def test_admin_can_view_any_order(
    client,
    auth_headers,
    users,
    create_order,
    sample_product,
):
    order = create_order(users["customer"], sample_product, status="pending")

    response = client.get(
        f"/api/orders/{order.id}",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200
    assert response.get_json()["id"] == order.id


def test_place_order_from_cart(
    client,
    auth_headers,
    users,
    create_cart_for_user,
    sample_product,
    app_ctx,
):
    sample_product.inventory.stock_quantity = 20
    db.session.commit()
    cart = create_cart_for_user(users["customer"], [(sample_product, 2)])

    response = client.post(
        "/api/orders",
        json={"delivery_address": "Pytest Address", "payment_method": "COD"},
        headers=auth_headers(users["customer"]),
    )

    data = response.get_json()
    order_id = data["order"]["id"]

    assert response.status_code == 201
    assert data["order"]["status"] == "pending"
    assert CartItem.query.filter_by(cart_id=cart.id).count() == 0
    assert Payment.query.filter_by(order_id=order_id).first() is not None


def test_approve_order_requires_admin(
    client,
    auth_headers,
    users,
    create_order,
    sample_product,
):
    order = create_order(users["customer"], sample_product, status="pending")

    response = client.post(
        f"/api/orders/{order.id}/approve",
        headers=auth_headers(users["customer"]),
    )

    assert response.status_code == 403


def test_approve_order_success(
    client,
    auth_headers,
    users,
    create_order,
    sample_product,
):
    order = create_order(users["customer"], sample_product, status="pending")

    response = client.post(
        f"/api/orders/{order.id}/approve",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200
    assert Order.query.get(order.id).status == "approved"


def test_assign_packer_to_approved_order(
    client,
    auth_headers,
    users,
    create_order,
    sample_product,
):
    order = create_order(users["customer"], sample_product, status="approved")

    response = client.post(
        f"/api/orders/{order.id}/assign-packer",
        json={"packer_id": users["packer"].id},
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200
    assert Order.query.get(order.id).status == "packing"


def test_get_order_status_returns_steps(
    client,
    auth_headers,
    users,
    create_order,
    sample_product,
):
    order = create_order(users["customer"], sample_product, status="pending")

    response = client.get(
        f"/api/orders/{order.id}/status",
        headers=auth_headers(users["customer"]),
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data["current_status"] == "pending"
    assert len(data["steps"]) >= 6


def test_cancel_order_by_customer(
    client,
    auth_headers,
    users,
    create_order,
    sample_product,
):
    order = create_order(users["customer"], sample_product, status="pending")

    response = client.post(
        f"/api/orders/{order.id}/cancel",
        headers=auth_headers(users["customer"]),
    )

    assert response.status_code == 200
    assert Order.query.get(order.id).status == "cancelled"
