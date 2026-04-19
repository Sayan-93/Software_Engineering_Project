from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from models import db
from models.models import (
    Order, User, Inventory, SalesAnalytics, Product
)
from sqlalchemy import func
from datetime import date

admin_bp = Blueprint("admin", __name__)


def admin_required(claims):
    return claims.get("role") == "admin"


@admin_bp.route("/admin/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    claims = get_jwt()
    if not admin_required(claims):
        return jsonify({"error": "Admin access required"}), 403

    pending_orders = Order.query.filter_by(status="pending").count()
    packing_orders = Order.query.filter_by(status="packing").count()
    out_for_delivery = Order.query.filter_by(status="out_for_delivery").count()

    low_stock = [
        i for i in Inventory.query.all()
        if i.stock_quantity < i.reorder_level
    ]

    today_orders = Order.query.filter(
        func.date(Order.created_at) == date.today()
    ).all()

    today_revenue = sum(
        row.revenue for row in SalesAnalytics.query.filter_by(date=date.today()).all()
    )

    return jsonify({
        "pending_orders": pending_orders,
        "packing_orders": packing_orders,
        "out_for_delivery": out_for_delivery,
        "low_stock_count": len(low_stock),
        "low_stock_items": [i.to_dict() for i in low_stock],
        "today_orders": len(today_orders),
        "today_revenue": round(today_revenue, 2)
    }), 200


@admin_bp.route("/admin/users", methods=["GET"])
@jwt_required()
def get_users():
    claims = get_jwt()
    if not admin_required(claims):
        return jsonify({"error": "Admin access required"}), 403

    role = request.args.get("role")
    query = User.query
    if role:
        query = query.filter_by(role=role)

    users = query.all()
    return jsonify([u.to_dict() for u in users]), 200

@admin_bp.route("/admin/orders/assign-packer", methods=["POST"])
@jwt_required()
def assign_packer():
    claims = get_jwt()
    if not admin_required(claims):
        return jsonify({"error": "Admin access required"}), 403

    data = request.get_json()
    order_id = data.get("order_id")
    packer_id = data.get("packer_id")

    # ✅ Validate input
    if not order_id or not packer_id:
        return jsonify({"error": "order_id and packer_id are required"}), 400

    # ✅ Use modern SQLAlchemy (fixes warning)
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    # ✅ Business rule check
    if order.status != "approved":
        return jsonify({
            "error": "Order must be approved before assigning packer"
        }), 400

    packer = db.session.get(User, packer_id)
    if not packer or packer.role != "packer":
        return jsonify({"error": "Invalid packer"}), 400

    from models.models import PackingAssignment, OrderStatusHistory

    # ✅ Prevent duplicate assignment
    existing = PackingAssignment.query.filter_by(order_id=order_id).first()
    if existing:
        return jsonify({"error": "Packer already assigned"}), 409

    # ✅ Create assignment
    assignment = PackingAssignment(
        order_id=order_id,
        packer_id=packer_id,
        status="assigned"
    )
    db.session.add(assignment)

    # ✅ Track order status history
    history = OrderStatusHistory(
        order_id=order.id,
        status="packing"
    )
    db.session.add(history)

    # ✅ Update order status
    order.status = "packing"

    # ✅ Commit all changes
    db.session.commit()

    return jsonify({
        "message": "Packer assigned successfully"
    }), 200


@admin_bp.route("/admin/packers", methods=["GET"])
@jwt_required()
def get_packers():
    claims = get_jwt()
    if not admin_required(claims):
        return jsonify({"error": "Admin access required"}), 403

    packers = User.query.filter_by(role="packer").all()
    return jsonify([u.to_dict() for u in packers]), 200

@admin_bp.route("/admin/orders/export-pdf", methods=["GET"])
@jwt_required()
def export_orders_pdf():
    from flask import make_response, jsonify
    from flask_jwt_extended import get_jwt   # ✅ FIXED IMPORT
    import io
    from datetime import datetime, date

    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Admin access required"}), 403

    # ✅ ONLY PENDING ORDERS
    orders = Order.query.filter_by(status="pending") \
        .order_by(Order.created_at.desc()) \
        .all()

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    except ImportError:
        return jsonify({"error": "reportlab not installed"}), 500

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=25,
        rightMargin=25,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "title",
        parent=styles["Normal"],
        fontSize=18,
        fontName="Helvetica-Bold",
        textColor=colors.grey
    )

    subtitle_style = ParagraphStyle(
        "subtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.grey
    )

    header_style = ParagraphStyle(
        "header",
        parent=styles["Normal"],
        fontSize=10,
        fontName="Helvetica-Bold",
        textColor=colors.green
    )

    cell_style = ParagraphStyle(
        "cell",
        parent=styles["Normal"],
        fontSize=9,
        leading=12
    )

    story = []

    # HEADER
    story.append(Paragraph("FreshMart Delivery Order List", title_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Pending Orders Only", subtitle_style))
    story.append(Spacer(1, 14))

    generated = datetime.now().strftime("%d %b %Y, %I:%M %p")

    meta_table = Table([[
        "Status: pending",
        f"Total Orders: {len(orders)}",
        f"Generated: {generated}"
    ]], colWidths=[150, 150, 200])

    meta_table.setStyle(TableStyle([
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))

    story.append(meta_table)
    story.append(Spacer(1, 12))

    # MAIN TABLE HEADER
    table_data = [[
        Paragraph("S.NO", header_style),
        Paragraph("NAME", header_style),
        Paragraph("FLAT NO", header_style),
        Paragraph("PHONE", header_style),
        Paragraph("ADDRESS", header_style),
        Paragraph("ORDER", header_style),
    ]]

    serial = 1

    for order in orders:
        # ✅ SAFE CUSTOMER HANDLING
        customer = order.customer if order.customer else None

        customer_name = customer.name if customer and customer.name else "-"
        phone = customer.phone if customer and customer.phone else "-"
        flat_no = customer.flat_unit_number if customer and customer.flat_unit_number else "-"
        address = order.delivery_address if order.delivery_address else "-"

        # INNER ORDER TABLE
        inner_data = [[
            Paragraph("S.NO", cell_style),
            Paragraph("ITEM", cell_style),
            Paragraph("QTY", cell_style),
        ]]

        item_serial = 1

        for item in order.items:
            # ✅ SAFE PRODUCT HANDLING
            product = item.product if item.product else None

            product_name = product.name if product and product.name else "Item"
            unit = product.unit if product and product.unit else ""
            qty = item.quantity if item.quantity else 0

            inner_data.append([
                Paragraph(str(item_serial), cell_style),
                Paragraph(f"{product_name} ({unit})", cell_style),
                Paragraph(str(qty), cell_style),
            ])

            item_serial += 1

        inner_table = Table(inner_data, colWidths=[25, 100, 35])

        inner_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))

        table_data.append([
            Paragraph(str(serial), cell_style),
            Paragraph(customer_name, cell_style),
            Paragraph(flat_no, cell_style),
            Paragraph(phone, cell_style),
            Paragraph(address, cell_style),
            inner_table
        ])

        serial += 1

    # MAIN TABLE
    table = Table(table_data, colWidths=[25, 90, 70, 80, 120, 150])

    table.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (-1, 0), 1, colors.green),
        ("LINEBELOW", (0, 1), (-1, -1), 0.25, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    story.append(table)

    doc.build(story)
    buffer.seek(0)

    response = make_response(buffer.read())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"attachment; filename=freshmart_pending_orders_{date.today()}.pdf"

    return response