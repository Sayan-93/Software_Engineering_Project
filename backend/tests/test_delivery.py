from models.models import DeliveryAssignment, Order, Payment


def test_get_deliveries_success(
    client,
    auth_headers,
    users,
    create_order,
    assign_delivery_person,
    sample_product,
):
    order = create_order(users["customer"], sample_product, status="out_for_delivery")
    assign_delivery_person(order, users["delivery"], status="out_for_delivery")

    response = client.get(
        "/api/delivery/orders",
        headers=auth_headers(users["delivery"]),
    )

    assert response.status_code == 200
    assert any(item["order_id"] == order.id for item in response.get_json())


def test_get_deliveries_forbidden(client, auth_headers, users):
    response = client.get(
        "/api/delivery/orders",
        headers=auth_headers(users["customer"]),
    )

    assert response.status_code == 403


def test_update_delivery_status_success(
    client,
    auth_headers,
    users,
    create_order,
    assign_delivery_person,
    sample_product,
):
    order = create_order(users["customer"], sample_product, status="packed")
    assign_delivery_person(order, users["delivery"], status="assigned")

    response = client.post(
        "/api/delivery/update",
        headers=auth_headers(users["delivery"]),
        json={"order_id": order.id, "status": "out_for_delivery"},
    )

    assert response.status_code == 200
    assert DeliveryAssignment.query.filter_by(order_id=order.id).first().status == "out_for_delivery"
    assert Order.query.get(order.id).status == "out_for_delivery"


def test_update_delivery_status_invalid_status(
    client,
    auth_headers,
    users,
    create_order,
    assign_delivery_person,
    sample_product,
):
    order = create_order(users["customer"], sample_product, status="packed")
    assign_delivery_person(order, users["delivery"], status="assigned")

    response = client.post(
        "/api/delivery/update",
        headers=auth_headers(users["delivery"]),
        json={"order_id": order.id, "status": "invalid_status"},
    )

    assert response.status_code == 400


def test_update_delivery_status_missing_fields(client, auth_headers, users):
    response = client.post(
        "/api/delivery/update",
        headers=auth_headers(users["delivery"]),
        json={},
    )

    assert response.status_code == 400


def test_update_delivery_status_assignment_not_found(client, auth_headers, users):
    response = client.post(
        "/api/delivery/update",
        headers=auth_headers(users["delivery"]),
        json={"order_id": 99999, "status": "picked_up"},
    )

    assert response.status_code == 404


def test_update_delivery_status_delivered_marks_cod_payment_paid(
    client,
    auth_headers,
    users,
    create_order,
    assign_delivery_person,
    sample_product,
):
    order = create_order(
        users["customer"],
        sample_product,
        status="out_for_delivery",
        payment_method="COD",
        payment_status="pending",
    )
    assign_delivery_person(order, users["delivery"], status="out_for_delivery")

    response = client.post(
        "/api/delivery/update",
        headers=auth_headers(users["delivery"]),
        json={"order_id": order.id, "status": "delivered"},
    )

    payment = Payment.query.filter_by(order_id=order.id).first()
    assignment = DeliveryAssignment.query.filter_by(order_id=order.id).first()

    assert response.status_code == 200
    assert assignment.status == "delivered"
    assert payment.payment_status == "paid"
