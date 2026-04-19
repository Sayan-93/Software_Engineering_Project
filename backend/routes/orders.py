from datetime import datetime, date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db
from models.models import (
    Order, OrderItem, OrderStatusHistory, Payment,
    Cart, CartItem, Inventory, SalesAnalytics
)

orders_bp = Blueprint("orders", __name__)


def push_status(order, status):
    """Record status change in history."""
    history = OrderStatusHistory(order_id=order.id, status=status)
    db.session.add(history)
    order.status = status


@orders_bp.route("/orders", methods=["GET"])
@jwt_required()
def get_orders():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role")

    if role == "admin":
        orders = Order.query.order_by(Order.created_at.desc()).all()
    else:
        orders = Order.query.filter_by(customer_id=user_id).order_by(Order.created_at.desc()).all()

    return jsonify([o.to_dict() for o in orders]), 200


@orders_bp.route("/orders/<int:order_id>", methods=["GET"])
@jwt_required()
def get_order(order_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role")

    order = Order.query.get_or_404(order_id)

    if role not in ("admin", "packer", "delivery") and order.customer_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    return jsonify(order.to_dict(with_items=True)), 200


@orders_bp.route("/orders", methods=["POST"])
@jwt_required()
def place_order():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    delivery_address = data.get("delivery_address", "")
    payment_method = data.get("payment_method", "COD")

    cart = Cart.query.filter_by(customer_id=user_id).first()
    if not cart or not cart.items:
        return jsonify({"error": "Cart is empty"}), 400

    total = 0
    order_items = []

    for cart_item in cart.items:
        product = cart_item.product
        if not product or not product.is_active:
            continue

        inv = product.inventory
        if inv and inv.stock_quantity < cart_item.quantity:
            return jsonify({"error": f"Insufficient stock for {product.name}"}), 400

        price = product.price * (1 - product.discount / 100)
        total += price * cart_item.quantity
        order_items.append((product, cart_item.quantity, price))

    if not order_items:
        return jsonify({"error": "No valid items"}), 400

    order = Order(
        customer_id=user_id,
        total_amount=round(total, 2),
        status="pending",
        payment_status="pending",
        delivery_address=delivery_address
    )
    db.session.add(order)
    db.session.flush()

    for product, qty, price in order_items:
        oi = OrderItem(order_id=order.id, product_id=product.id, quantity=qty, price=price)
        db.session.add(oi)

        # Deduct from inventory
        inv = product.inventory
        if inv:
            inv.stock_quantity -= qty
            inv.last_updated = datetime.utcnow()

        # Record sales analytics
        analytics = SalesAnalytics(
            product_id=product.id,
            quantity_sold=qty,
            date=date.today(),
            revenue=price * qty
        )
        db.session.add(analytics)

    # Create payment record
    payment = Payment(
        order_id=order.id,
        amount=total,
        payment_method=payment_method,
        payment_status="pending"
    )
    db.session.add(payment)

    # Push initial status
    push_status(order, "pending")

    # Clear the cart
    CartItem.query.filter_by(cart_id=cart.id).delete()

    db.session.commit()
    return jsonify({"message": "Order placed successfully", "order": order.to_dict(with_items=True)}), 201


@orders_bp.route("/orders/<int:order_id>/approve", methods=["POST"])
@jwt_required()
def approve_order(order_id):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    order = Order.query.get_or_404(order_id)

    if order.status != "pending":
        return jsonify({"error": f"Cannot approve order with status '{order.status}'"}), 400

    push_status(order, "approved")
    db.session.commit()
    return jsonify({"message": "Order approved", "order": order.to_dict()}), 200


@orders_bp.route("/orders/<int:order_id>/assign-packer", methods=["POST"])
@jwt_required()
def assign_packer(order_id):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    data = request.get_json()
    packer_id = data.get("packer_id")

    if not packer_id:
        return jsonify({"error": "packer_id is required"}), 400

    order = Order.query.get_or_404(order_id)

    if order.status != "approved":
        return jsonify({"error": "Order must be approved first"}), 400

    from models.models import PackingAssignment, User
    packer = User.query.get(packer_id)
    if not packer or packer.role != "packer":
        return jsonify({"error": "Invalid packer"}), 400

    assignment = PackingAssignment(order_id=order.id, packer_id=packer_id, status="assigned")
    db.session.add(assignment)
    push_status(order, "packing")
    db.session.commit()

    return jsonify({"message": "Packer assigned", "order": order.to_dict()}), 200


@orders_bp.route("/orders/<int:order_id>/status", methods=["GET"])
@jwt_required()
def get_order_status(order_id):
    order = Order.query.get_or_404(order_id)

    history = OrderStatusHistory.query.filter_by(order_id=order_id)\
        .order_by(OrderStatusHistory.updated_at.asc()).all()

    all_steps = ["pending", "approved", "packing", "packed", "out_for_delivery", "delivered"]
    completed = {h.status for h in history}

    steps = [{"label": s, "done": s in completed} for s in all_steps]

    return jsonify({
        "order_id": order.id,
        "current_status": order.status,
        "steps": steps
    }), 200


@orders_bp.route("/orders/<int:order_id>/cancel", methods=["POST"])
@jwt_required()
def cancel_order(order_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role")

    order = Order.query.get_or_404(order_id)

    if role != "admin" and order.customer_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    if order.status in ("packed", "out_for_delivery", "delivered"):
        return jsonify({"error": "Cannot cancel order at this stage"}), 400

    push_status(order, "cancelled")
    db.session.commit()
    return jsonify({"message": "Order cancelled"}), 200

