from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models import db
from models.models import DeliveryAssignment, Order, OrderStatusHistory

delivery_bp = Blueprint("delivery", __name__)

VALID_STATUSES = ("picked_up", "out_for_delivery", "delivered")


def push_status(order, status):
    history = OrderStatusHistory(order_id=order.id, status=status)
    db.session.add(history)
    order.status = status


@delivery_bp.route("/delivery/orders", methods=["GET"])
@jwt_required()
def get_deliveries():
    user_id = int(get_jwt_identity())
    claims = get_jwt()

    if claims.get("role") != "delivery":
        return jsonify({"error": "Delivery access required"}), 403

    assignments = DeliveryAssignment.query.filter_by(delivery_person_id=user_id).all()

    result = []
    for a in assignments:
        order = a.order
        customer = order.customer
        result.append({
            "assignment_id": a.id,
            "order_id": order.id,
            "status": a.status,
            "assigned_at": str(a.assigned_at),
            "delivered_at": str(a.delivered_at) if a.delivered_at else None,
            "customer": customer.name if customer else None,
            "phone": customer.phone if customer else None,
            "address": order.delivery_address,
            "items": [i.to_dict() for i in order.items],
            "total_amount": order.total_amount
        })

    return jsonify(result), 200


@delivery_bp.route("/delivery/update", methods=["POST"])
@jwt_required()
def update_delivery_status():
    user_id = int(get_jwt_identity())
    claims = get_jwt()

    if claims.get("role") != "delivery":
        return jsonify({"error": "Delivery access required"}), 403

    data = request.get_json()
    order_id = data.get("order_id")
    new_status = data.get("status")

    if not order_id or not new_status:
        return jsonify({"error": "order_id and status are required"}), 400

    if new_status not in VALID_STATUSES:
        return jsonify({"error": f"Status must be one of: {VALID_STATUSES}"}), 400

    assignment = DeliveryAssignment.query.filter_by(
        order_id=order_id, delivery_person_id=user_id
    ).first()

    if not assignment:
        return jsonify({"error": "Assignment not found"}), 404

    assignment.status = new_status

    order = Order.query.get(order_id)

    if new_status == "delivered":
        assignment.delivered_at = datetime.utcnow()
        push_status(order, "delivered")
        # Mark payment as paid for COD
        if order.payment and order.payment.payment_method == "COD":
            order.payment.payment_status = "paid"
    elif new_status == "out_for_delivery":
        push_status(order, "out_for_delivery")
    elif new_status == "picked_up":
        # Just update assignment status, order status stays
        pass

    db.session.commit()
    return jsonify({"message": f"Status updated to {new_status}"}), 200
