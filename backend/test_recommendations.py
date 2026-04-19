from app import app
from models.models import Product


def test_recommendations_endpoint_returns_ranked_products():
    client = app.test_client()

    with app.app_context():
        product = Product.query.filter_by(is_active=True).first()
        assert product is not None

    response = client.get(f"/api/products/{product.id}/recommendations")

    assert response.status_code == 200
    recommendations = response.get_json()

    assert isinstance(recommendations, list)
    assert recommendations
    assert all(item["id"] != product.id for item in recommendations)
