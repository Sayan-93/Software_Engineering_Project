from models import db
from models.models import Category, Inventory, Product


def test_get_products_returns_active_products(client):
    response = client.get("/api/products")

    assert response.status_code == 200
    assert any(product["name"] == "Apple" for product in response.get_json())


def test_get_products_supports_search(client):
    response = client.get("/api/products?search=apple")

    assert response.status_code == 200
    assert all("apple" in product["name"].lower() for product in response.get_json())


def test_get_single_product(client, sample_product):
    response = client.get(f"/api/products/{sample_product.id}")

    assert response.status_code == 200
    assert response.get_json()["id"] == sample_product.id


def test_add_product_requires_admin(client, auth_headers, users):
    response = client.post(
        "/api/products",
        json={"name": "Forbidden Product", "price": 10},
        headers=auth_headers(users["customer"]),
    )

    assert response.status_code == 403


def test_add_product_creates_inventory(client, auth_headers, users, app_ctx):
    category = Category.query.first()

    response = client.post(
        "/api/products",
        json={
            "name": "Pytest Papaya",
            "price": 55,
            "category_id": category.id,
            "unit": "kg",
        },
        headers=auth_headers(users["admin"]),
    )

    data = response.get_json()
    product_id = data["product"]["id"]

    assert response.status_code == 201
    assert Inventory.query.filter_by(product_id=product_id).first() is not None


def test_update_product(client, auth_headers, users, sample_product):
    response = client.put(
        f"/api/products/{sample_product.id}",
        json={"price": 135, "discount": 12},
        headers=auth_headers(users["admin"]),
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data["product"]["price"] == 135.0
    assert data["product"]["discount"] == 12.0


def test_delete_product_soft_deactivates(client, auth_headers, users, app_ctx, cleanup):
    category = Category.query.first()
    product = cleanup(Product(
        name="Pytest Delete Product",
        price=10,
        category_id=category.id,
        unit="kg",
        is_active=True,
    ))
    inventory = cleanup(Inventory(product=product, stock_quantity=1, reorder_level=1))

    db.session.add_all([product, inventory])
    db.session.commit()

    response = client.delete(
        f"/api/products/{product.id}",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200
    assert Product.query.get(product.id).is_active is False


def test_get_categories(client):
    response = client.get("/api/categories")

    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_add_category(client, auth_headers, users):
    response = client.post(
        "/api/categories",
        json={"name": "Pytest Category", "description": "Temp"},
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 201
    assert response.get_json()["category"]["name"] == "Pytest Category"
