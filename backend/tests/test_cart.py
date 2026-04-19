from models import db
from models.models import CartItem


def test_get_cart(client, auth_headers, users):
    response = client.get("/api/cart", headers=auth_headers(users["customer"]))

    assert response.status_code == 200
    assert "items" in response.get_json()


def test_add_to_cart(client, auth_headers, users, sample_product):
    response = client.post(
        "/api/cart",
        json={"product_id": sample_product.id, "quantity": 2},
        headers=auth_headers(users["customer"]),
    )

    assert response.status_code == 201
    assert response.get_json()["message"] == "Item added to cart"


def test_update_cart_item(client, auth_headers, users, create_cart_for_user, sample_product):
    cart = create_cart_for_user(users["customer"], [(sample_product, 1)])
    item = CartItem.query.filter_by(cart_id=cart.id, product_id=sample_product.id).first()

    response = client.put(
        f"/api/cart/{item.id}",
        json={"quantity": 5},
        headers=auth_headers(users["customer"]),
    )

    assert response.status_code == 200
    assert CartItem.query.get(item.id).quantity == 5


def test_remove_from_cart(client, auth_headers, users, create_cart_for_user, sample_product):
    cart = create_cart_for_user(users["customer"], [(sample_product, 1)])
    item = CartItem.query.filter_by(cart_id=cart.id, product_id=sample_product.id).first()

    response = client.delete(
        f"/api/cart/{item.id}",
        headers=auth_headers(users["customer"]),
    )

    assert response.status_code == 200
    assert CartItem.query.get(item.id) is None


def test_clear_cart(client, auth_headers, users, create_cart_for_user, sample_product, another_product):
    cart = create_cart_for_user(users["customer"], [(sample_product, 2), (another_product, 2)])

    response = client.delete("/api/cart/clear", headers=auth_headers(users["customer"]))

    assert response.status_code == 200
    assert response.get_json()["message"] == "Cart cleared"
    assert CartItem.query.filter_by(cart_id=cart.id).count() == 0
