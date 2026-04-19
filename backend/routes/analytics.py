from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from models import db
from models.models import SalesAnalytics, StockForecast, Product
from sqlalchemy import func
from datetime import date, timedelta

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/analytics/sales", methods=["GET"])
@jwt_required()
def sales_summary():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    # Last 7 days breakdown
    days = []
    for i in range(6, -1, -1):
        d = date.today() - timedelta(days=i)
        rows = SalesAnalytics.query.filter_by(date=d).all()
        days.append({
            "date": str(d),
            "label": d.strftime("%a"),
            "revenue": round(sum(r.revenue for r in rows), 2),
            "quantity_sold": sum(r.quantity_sold for r in rows)
        })

    total_revenue = db.session.query(func.sum(SalesAnalytics.revenue)).scalar() or 0
    total_sold = db.session.query(func.sum(SalesAnalytics.quantity_sold)).scalar() or 0

    return jsonify({
        "last_7_days": days,
        "total_revenue": round(total_revenue, 2),
        "total_quantity_sold": total_sold
    }), 200


@analytics_bp.route("/analytics/top-products", methods=["GET"])
@jwt_required()
def top_products():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    limit = int(request.args.get("limit", 5))

    rows = db.session.query(
        SalesAnalytics.product_id,
        func.sum(SalesAnalytics.quantity_sold).label("total_qty"),
        func.sum(SalesAnalytics.revenue).label("total_revenue")
    ).group_by(SalesAnalytics.product_id)\
     .order_by(func.sum(SalesAnalytics.revenue).desc())\
     .limit(limit).all()

    result = []
    for row in rows:
        product = Product.query.get(row.product_id)
        result.append({
            "product_id": row.product_id,
            "product_name": product.name if product else "Unknown",
            "total_qty": row.total_qty,
            "total_revenue": round(row.total_revenue, 2)
        })

    return jsonify(result), 200


@analytics_bp.route("/analytics/forecast", methods=["GET"])
@jwt_required()
def get_forecast():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    forecasts = StockForecast.query.order_by(StockForecast.forecast_date.asc()).all()
    return jsonify([f.to_dict() for f in forecasts]), 200
