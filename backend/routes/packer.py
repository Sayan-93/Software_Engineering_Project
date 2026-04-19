from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db
from models.models import (
    PackingAssignment, DeliveryAssignment, Order,
    OrderStatusHistory, User
)

packer_bp = Blueprint("packer", __name__)


def push_status(order, status):
    history = OrderStatusHistory(order_id=order.id, status=status)
    db.session.add(history)
    order.status = status


@packer_bp.route("/packer/orders", methods=["GET"])
@jwt_required()
def get_assigned_orders():
    user_id = int(get_jwt_identity())
    claims = get_jwt()

    if claims.get("role") != "packer":
        return jsonify({"error": "Packer access required"}), 403

    assignments = PackingAssignment.query.filter_by(packer_id=user_id).all()

    result = []
    for a in assignments:
        order = a.order
        result.append({
            "assignment_id": a.id,
            "order_id": order.id,
            "status": a.status,
            "assigned_at": str(a.assigned_at),
            "customer": order.customer.name if order.customer else None,
            "delivery_address": order.delivery_address,
            "items": [i.to_dict() for i in order.items]
        })

    return jsonify(result), 200


@packer_bp.route("/packer/orders/<int:order_id>/packed", methods=["POST"])
@jwt_required()
def mark_packed(order_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()

    if claims.get("role") != "packer":
        return jsonify({"error": "Packer access required"}), 403

    assignment = PackingAssignment.query.filter_by(order_id=order_id, packer_id=user_id).first()
    if not assignment:
        return jsonify({"error": "Assignment not found"}), 404

    assignment.status = "packed"
    assignment.packed_at = datetime.utcnow()

    order = Order.query.get(order_id)
    push_status(order, "packed")

    db.session.commit()
    return jsonify({"message": "Order marked as packed"}), 200


@packer_bp.route("/assign-delivery", methods=["POST"])
@jwt_required()
def assign_delivery():
    user_id = int(get_jwt_identity())
    claims = get_jwt()

    if claims.get("role") != "packer":
        return jsonify({"error": "Packer access required"}), 403

    data = request.get_json()
    order_id = data.get("order_id")
    delivery_person_id = data.get("delivery_person_id")

    if not order_id or not delivery_person_id:
        return jsonify({"error": "order_id and delivery_person_id are required"}), 400

    order = Order.query.get_or_404(order_id)

    if order.status != "packed":
        return jsonify({"error": "Order must be packed before assigning delivery"}), 400

    delivery_person = User.query.get(delivery_person_id)
    if not delivery_person or delivery_person.role != "delivery":
        return jsonify({"error": "Invalid delivery person"}), 400

    # Check if already assigned
    existing = DeliveryAssignment.query.filter_by(order_id=order_id).first()
    if existing:
        return jsonify({"error": "Delivery already assigned"}), 409

    assignment = DeliveryAssignment(
        order_id=order_id,
        delivery_person_id=delivery_person_id,
        status="assigned"
    )
    db.session.add(assignment)
    push_status(order, "out_for_delivery")
    db.session.commit()

    return jsonify({"message": "Delivery person assigned successfully"}), 200


@packer_bp.route("/users/delivery-staff", methods=["GET"])
@jwt_required()
def get_delivery_staff():
    claims = get_jwt()
    if claims.get("role") not in ("admin", "packer"):
        return jsonify({"error": "Unauthorized"}), 403

    staff = User.query.filter_by(role="delivery").all()
    return jsonify([u.to_dict() for u in staff]), 200
