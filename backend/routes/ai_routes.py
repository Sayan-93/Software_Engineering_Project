from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

ai_bp = Blueprint("ai", __name__)


@ai_bp.route("/products/<int:product_id>/recommendations", methods=["GET"])
def get_recommendations(product_id):
    from ai.recommendations import get_recommendations_for_product
    recs = get_recommendations_for_product(product_id)
    return jsonify(recs), 200


@ai_bp.route("/ai/rebuild-recommendations", methods=["POST"])
@jwt_required()
def rebuild_recommendations():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    from ai.recommendations import build_recommendations
    build_recommendations()
    return jsonify({"message": "Recommendations rebuilt successfully"}), 200


@ai_bp.route("/ai/run-forecast", methods=["POST"])
@jwt_required()
def run_forecast():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    from ai.forecasting import forecast_stock
    forecast_stock()
    return jsonify({"message": "Stock forecast updated successfully"}), 200



