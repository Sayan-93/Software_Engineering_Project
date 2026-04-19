from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db
from models.models import Cart, CartItem, Product

cart_bp = Blueprint("cart", __name__)


def get_or_create_cart(customer_id):
    cart = Cart.query.filter_by(customer_id=customer_id).first()
    if not cart:
        cart = Cart(customer_id=customer_id)
        db.session.add(cart)
        db.session.commit()
    return cart


@cart_bp.route("/cart", methods=["GET"])
@jwt_required()
def get_cart():
    user_id = int(get_jwt_identity())
    cart = get_or_create_cart(user_id)
    return jsonify({
        "cart_id": cart.id,
        "items": [item.to_dict() for item in cart.items]
    }), 200


@cart_bp.route("/cart", methods=["POST"])
@jwt_required()
def add_to_cart():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    product_id = data.get("product_id")
    quantity = int(data.get("quantity", 1))
    selected_weight = data.get("selected_weight")  # e.g. "500g"
    price = data.get("price")                       # discounted price for selected weight

    if not product_id:
        return jsonify({"error": "product_id is required"}), 400

    product = Product.query.get(product_id)
    if not product or not product.is_active:
        return jsonify({"error": "Product not found"}), 404

    # Compute price if not provided by client
    if price is None:
        price = product.price
    price = float(price)

    cart = get_or_create_cart(user_id)

    # Match on product_id + selected_weight so different weights are separate line items
    existing = CartItem.query.filter_by(
        cart_id=cart.id,
        product_id=product_id,
        selected_weight=selected_weight
    ).first()

    if existing:
        existing.quantity += quantity
    else:
        item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            quantity=quantity,
            selected_weight=selected_weight,
            price=price
        )
        db.session.add(item)

    db.session.commit()
    return jsonify({"message": "Item added to cart"}), 201


@cart_bp.route("/cart/<int:item_id>", methods=["PUT"])
@jwt_required()
def update_cart_item(item_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    quantity = int(data.get("quantity", 1))

    item = CartItem.query.get_or_404(item_id)

    # Make sure the item belongs to the user
    if item.cart.customer_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    if quantity <= 0:
        db.session.delete(item)
    else:
        item.quantity = quantity

    db.session.commit()
    return jsonify({"message": "Cart updated"}), 200


@cart_bp.route("/cart/<int:item_id>", methods=["DELETE"])
@jwt_required()
def remove_from_cart(item_id):
    user_id = int(get_jwt_identity())
    item = CartItem.query.get_or_404(item_id)

    if item.cart.customer_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Item removed"}), 200


@cart_bp.route("/cart/clear", methods=["DELETE"])
@jwt_required()
def clear_cart():
    user_id = int(get_jwt_identity())
    cart = Cart.query.filter_by(customer_id=user_id).first()
    if cart:
        CartItem.query.filter_by(cart_id=cart.id).delete()
        db.session.commit()
    return jsonify({"message": "Cart cleared"}), 200
