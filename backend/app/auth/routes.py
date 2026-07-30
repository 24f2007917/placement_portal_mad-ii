from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.extensions import db
from app.models import User, Company, Student

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    role = data.get("role")
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if role not in ("student", "company"):
        return jsonify({"error": "role must be student or company"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email already registered"}), 409

    from werkzeug.security import generate_password_hash
    user = User(name=name, email=email, password_hash=generate_password_hash(password), role=role)
    db.session.add(user)
    db.session.flush()  # gives user.id before commit

    if role == "student":
        db.session.add(Student(user_id=user.id))
    else:
        db.session.add(Company(user_id=user.id, company_name=data.get("company_name", name)))

    db.session.commit()
    return jsonify({"message": "registered successfully"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    from werkzeug.security import check_password_hash
    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "invalid credentials"}), 401

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role, "name": user.name})
    return jsonify({"access_token": token, "role": user.role, "name": user.name}), 200