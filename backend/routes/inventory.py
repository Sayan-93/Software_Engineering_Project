from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from models import db
from models.models import Inventory

inventory_bp = Blueprint("inventory", __name__)


@inventory_bp.route("/inventory", methods=["GET"])
@jwt_required()
def get_inventory():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    items = Inventory.query.all()
    return jsonify([i.to_dict() for i in items]), 200


@inventory_bp.route("/inventory/<int:inventory_id>", methods=["PUT"])
@jwt_required()
def update_inventory(inventory_id):
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    inv = Inventory.query.get_or_404(inventory_id)
    data = request.get_json()

    if "stock_quantity" in data:
        inv.stock_quantity = int(data["stock_quantity"])
    if "reorder_level" in data:
        inv.reorder_level = int(data["reorder_level"])

    inv.last_updated = datetime.utcnow()
    db.session.commit()

    return jsonify({"message": "Inventory updated", "inventory": inv.to_dict()}), 200


@inventory_bp.route("/inventory/low-stock", methods=["GET"])
@jwt_required()
def low_stock_alerts():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    items = Inventory.query.all()
    low = [i.to_dict() for i in items if i.stock_quantity < i.reorder_level]
    return jsonify(low), 200
