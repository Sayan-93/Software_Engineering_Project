import os
import sys
import uuid

import pytest
from flask_jwt_extended import create_access_token
from sqlalchemy import inspect as sa_inspect


BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.append(BACKEND_DIR)

from app import app as flask_app
from models import db
from models.models import (
    Cart,
    CartItem,
    DeliveryAssignment,
    Order,
    OrderItem,
    OrderStatusHistory,
    PackingAssignment,
    Payment,
    Product,
    SalesAnalytics,
    StockForecast,
    User,
)
from seed import seed


@pytest.fixture(scope="session", autouse=True)
def seed_db():
    seed()


@pytest.fixture
def app():
    flask_app.config.update(
        {
            "TESTING": True,
            "JWT_SECRET_KEY": "this-is-a-very-secure-secret-key-at-least-32-characters",
        }
    )
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def app_ctx(app):
    with app.app_context():
        yield
        db.session.rollback()


@pytest.fixture(autouse=True)
def cleanup_orphan_assignments(app_ctx):
    valid_order_ids = {order.id for order in Order.query.all()}

    for assignment in PackingAssignment.query.all():
        if assignment.order_id not in valid_order_ids:
            db.session.delete(assignment)

    for assignment in DeliveryAssignment.query.all():
        if assignment.order_id not in valid_order_ids:
            db.session.delete(assignment)

    db.session.commit()


@pytest.fixture
def make_token(app):
    def _make_token(user):
        with app.app_context():
            return create_access_token(
                identity=str(user.id),
                additional_claims={"role": user.role},
            )

    return _make_token


@pytest.fixture
def get_user(app_ctx):
    def _get_user(email):
        return User.query.filter_by(email=email).first()

    return _get_user


@pytest.fixture
def auth_headers(make_token):
    def _auth_headers(user):
        return {"Authorization": f"Bearer {make_token(user)}"}

    return _auth_headers


@pytest.fixture
def users(get_user):
    return {
        "admin": get_user("admin@freshmart.com"),
        "customer": get_user("rahul@example.com"),
        "customer_two": get_user("asha@example.com"),
        "packer": get_user("kumar@freshmart.com"),
        "delivery": get_user("arun@freshmart.com"),
        "delivery_two": get_user("priya@freshmart.com"),
    }


@pytest.fixture
def sample_product(app_ctx):
    return Product.query.filter_by(name="Apple").first()


@pytest.fixture
def another_product(app_ctx):
    return Product.query.filter_by(name="Banana").first()


@pytest.fixture
def cleanup():
    created = []

    def _track(instance):
        created.append(instance)
        return instance

    yield _track

    for instance in reversed(created):
        state = sa_inspect(instance)
        identity = state.identity
        if not identity:
            continue

        obj = db.session.get(type(instance), identity[0])
        if obj is not None:
            db.session.delete(obj)
    db.session.commit()


@pytest.fixture
def unique_email():
    return f"pytest-{uuid.uuid4().hex[:8]}@example.com"


@pytest.fixture
def create_cart_for_user(app_ctx, cleanup):
    def _create_cart_for_user(user, items=None):
        cart = Cart.query.filter_by(customer_id=user.id).first()
        if cart:
            CartItem.query.filter_by(cart_id=cart.id).delete()
            db.session.commit()
        else:
            cart = cleanup(Cart(customer_id=user.id))
            db.session.add(cart)
            db.session.commit()

        items = items or []
        for product, quantity in items:
            item = cleanup(CartItem(cart_id=cart.id, product_id=product.id, quantity=quantity))
            db.session.add(item)
        db.session.commit()
        return cart

    return _create_cart_for_user


@pytest.fixture
def create_order(app_ctx, cleanup):
    def _create_order(
        customer,
        product,
        *,
        quantity=1,
        status="pending",
        payment_method="COD",
        payment_status="pending",
        delivery_address="Test Address",
    ):
        order = cleanup(
            Order(
                customer_id=customer.id,
                total_amount=round(product.price * quantity, 2),
                status=status,
                payment_status=payment_status,
                delivery_address=delivery_address,
            )
        )
        db.session.add(order)
        db.session.flush()

        order_item = cleanup(
            OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                price=product.price,
            )
        )
        payment = cleanup(
            Payment(
                order_id=order.id,
                amount=order.total_amount,
                payment_method=payment_method,
                payment_status=payment_status,
            )
        )
        history = cleanup(OrderStatusHistory(order_id=order.id, status=status))
        db.session.add_all([order_item, payment, history])
        db.session.commit()
        return order

    return _create_order


@pytest.fixture
def assign_packer(app_ctx, cleanup):
    def _assign_packer(order, packer, status="assigned"):
        assignment = cleanup(
            PackingAssignment(order_id=order.id, packer_id=packer.id, status=status)
        )
        db.session.add(assignment)
        db.session.commit()
        return assignment

    return _assign_packer


@pytest.fixture
def assign_delivery_person(app_ctx, cleanup):
    def _assign_delivery_person(order, delivery_person, status="assigned"):
        assignment = cleanup(
            DeliveryAssignment(
                order_id=order.id,
                delivery_person_id=delivery_person.id,
                status=status,
            )
        )
        db.session.add(assignment)
        db.session.commit()
        return assignment

    return _assign_delivery_person


@pytest.fixture
def cleanup_analytics(app_ctx):
    yield
    StockForecast.query.delete()
    db.session.commit()
