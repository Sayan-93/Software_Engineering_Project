from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from models import db
from models.models import Product, Category, Inventory
import json

products_bp = Blueprint("products", __name__)


@products_bp.route("/products", methods=["GET"])
def get_products():
    category_id = request.args.get("category_id")
    search = request.args.get("search", "")

    query = Product.query.filter_by(is_active=True)

    if category_id:
        query = query.filter_by(category_id=category_id)

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    products = query.all()
    return jsonify([p.to_dict() for p in products]), 200


@products_bp.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict()), 200


@products_bp.route("/products", methods=["POST"])
@jwt_required()
def add_product():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    data = request.get_json()
    name = data.get("name", "").strip()
    price = data.get("price")

    if not name or price is None:
        return jsonify({"error": "Name and price are required"}), 400

    product = Product(
        name=name,
        description=data.get("description", ""),
        category_id=data.get("category_id"),
        price=float(price),
        discount=float(data.get("discount", 0)),
        image_url=data.get("image_url", ""),
        unit=data.get("unit", "kg"),
        weight_options=json.dumps(data.get("weight_options", [])),
        weight_prices=json.dumps(data.get("weight_prices", {})),
        is_active=True
    )
    db.session.add(product)
    db.session.flush()

    # Auto-create inventory entry
    inventory = Inventory(product_id=product.id, stock_quantity=0, reorder_level=10)
    db.session.add(inventory)
    db.session.commit()

    return jsonify({"message": "Product added", "product": product.to_dict()}), 201


@products_bp.route("/products/<int:product_id>", methods=["PUT"])
@jwt_required()
def update_product(product_id):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    product = Product.query.get_or_404(product_id)
    data = request.get_json()

    product.name = data.get("name", product.name)
    product.description = data.get("description", product.description)
    product.category_id = data.get("category_id", product.category_id)
    product.price = float(data.get("price", product.price))
    product.discount = float(data.get("discount", product.discount))
    product.image_url = data.get("image_url", product.image_url)
    product.unit = data.get("unit", product.unit)
    product.is_active = data.get("is_active", product.is_active)
    if "weight_options" in data:
        product.weight_options = json.dumps(data.get("weight_options", []))
    if "weight_prices" in data:
        product.weight_prices = json.dumps(data.get("weight_prices", {}))

    db.session.commit()
    return jsonify({"message": "Product updated", "product": product.to_dict()}), 200


@products_bp.route("/products/<int:product_id>", methods=["DELETE"])
@jwt_required()
def delete_product(product_id):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    product = Product.query.get_or_404(product_id)
    product.is_active = False   # Soft delete
    db.session.commit()
    return jsonify({"message": "Product deactivated"}), 200


@products_bp.route("/categories", methods=["GET"])
def get_categories():
    cats = Category.query.all()
    return jsonify([c.to_dict() for c in cats]), 200


@products_bp.route("/categories", methods=["POST"])
@jwt_required()
def add_category():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    data = request.get_json()
    cat = Category(name=data["name"], description=data.get("description", ""))
    db.session.add(cat)
    db.session.commit()
    return jsonify({"message": "Category added", "category": cat.to_dict()}), 201
