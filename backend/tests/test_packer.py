from models.models import DeliveryAssignment, Order, PackingAssignment


def test_get_assigned_orders_for_packer(
    client,
    auth_headers,
    users,
    create_order,
    assign_packer,
    sample_product,
):
    order = create_order(users["customer"], sample_product, status="packing")
    assign_packer(order, users["packer"], status="assigned")

    response = client.get(
        "/api/packer/orders",
        headers=auth_headers(users["packer"]),
    )

    assert response.status_code == 200
    assert any(item["order_id"] == order.id for item in response.get_json())


def test_mark_packed_updates_assignment_and_order(
    client,
    auth_headers,
    users,
    create_order,
    assign_packer,
    sample_product,
):
    order = create_order(users["customer"], sample_product, status="packing")
    assign_packer(order, users["packer"], status="assigned")

    response = client.post(
        f"/api/packer/orders/{order.id}/packed",
        headers=auth_headers(users["packer"]),
    )

    assignment = PackingAssignment.query.filter_by(order_id=order.id).first()

    assert response.status_code == 200
    assert assignment.status == "packed"
    assert Order.query.get(order.id).status == "packed"


def test_assign_delivery_requires_packed_order(
    client,
    auth_headers,
    users,
    create_order,
    assign_packer,
    sample_product,
):
    order = create_order(users["customer"], sample_product, status="packing")
    assign_packer(order, users["packer"], status="assigned")

    response = client.post(
        "/api/assign-delivery",
        json={"order_id": order.id, "delivery_person_id": users["delivery"].id},
        headers=auth_headers(users["packer"]),
    )

    assert response.status_code == 400


def test_assign_delivery_success(
    client,
    auth_headers,
    users,
    create_order,
    assign_packer,
    sample_product,
):
    order = create_order(users["customer"], sample_product, status="packed")
    assign_packer(order, users["packer"], status="packed")

    response = client.post(
        "/api/assign-delivery",
        json={"order_id": order.id, "delivery_person_id": users["delivery"].id},
        headers=auth_headers(users["packer"]),
    )

    assignment = DeliveryAssignment.query.filter_by(order_id=order.id).first()

    assert response.status_code == 200
    assert assignment is not None
    assert Order.query.get(order.id).status == "out_for_delivery"


def test_get_delivery_staff_for_packer(client, auth_headers, users):
    response = client.get(
        "/api/users/delivery-staff",
        headers=auth_headers(users["packer"]),
    )

    data = response.get_json()

    assert response.status_code == 200
    assert any(member["role"] == "delivery" for member in data)
