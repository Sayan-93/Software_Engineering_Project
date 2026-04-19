from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from models import db
from models.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    name             = data.get("name", "").strip()
    email            = data.get("email", "").strip().lower()
    password         = data.get("password", "")
    role             = data.get("role", "customer")
    phone            = data.get("phone", "").strip()
    address          = data.get("address", "").strip()
    flat_unit_number = data.get("flat_unit_number", "").strip()

    # Core field validation
    if not name or not email or not password:
        return jsonify({"error": "Name, email and password are required"}), 400

    if role not in ("admin", "customer", "packer", "delivery"):
        return jsonify({"error": "Invalid role"}), 400

    # Customer-specific address fields are required
    if role == "customer":
        missing = []
        if not phone:            missing.append("phone")
        if not address:          missing.append("address")
        if not flat_unit_number: missing.append("flat_unit_number")
        if missing:
            return jsonify({"error": f"Required fields missing: {', '.join(missing)}"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    hashed = generate_password_hash(password)
    user = User(
        name=name,
        email=email,
        password=hashed,
        role=role,
        phone=phone,
        address=address,
        flat_unit_number=flat_unit_number,
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Registered successfully", "user": user.to_dict()}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})

    return jsonify({
        "token": token,
        "role": user.role,
        "user": user.to_dict()
    }), 200
