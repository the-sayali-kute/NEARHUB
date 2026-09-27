from flask import Blueprint, jsonify, request
from db import get_db_connection

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from flask_jwt_extended import create_access_token


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)


# =========================================================
# STUDENT REGISTRATION
# =========================================================
@auth_bp.route("/student/register", methods=["POST"])
def student_register():

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "Request body is required"
        }), 400

    required_fields = [
        "name",
        "email",
        "phone",
        "password",
        "gender",
        "college",
        "course",
        "year",
        "budget",
        "preferred_location"
    ]

    for field in required_fields:

        if field not in data:

            return jsonify({
                "message": f"{field} is required"
            }), 400

    # -----------------------------------------------------
    # BASIC VALIDATION
    # -----------------------------------------------------
    if not str(data["name"]).strip():

        return jsonify({
            "message": "Name cannot be empty"
        }), 400

    if not str(data["email"]).strip():

        return jsonify({
            "message": "Email cannot be empty"
        }), 400

    if not str(data["password"]):

        return jsonify({
            "message": "Password cannot be empty"
        }), 400

    try:
        budget = float(data["budget"])

    except (TypeError, ValueError):

        return jsonify({
            "message": "Budget must be a number"
        }), 400

    if budget < 0:

        return jsonify({
            "message": "Budget cannot be negative"
        }), 400

    connection = get_db_connection()

    try:

        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # CHECK EMAIL
        # -------------------------------------------------
        cursor.execute("""
            SELECT student_id
            FROM student
            WHERE email = %s
        """, (data["email"],))

        existing_student = cursor.fetchone()

        if existing_student:

            return jsonify({
                "message": "Email already registered"
            }), 409

        # -------------------------------------------------
        # HASH PASSWORD
        # -------------------------------------------------
        password_hash = generate_password_hash(
            data["password"]
        )

        # -------------------------------------------------
        # INSERT STUDENT
        # -------------------------------------------------
        cursor.execute("""
            INSERT INTO student
            (
                name,
                email,
                phone,
                password_hash,
                gender,
                college,
                course,
                year,
                budget,
                preferred_location
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """, (
            data["name"],
            data["email"],
            data["phone"],
            password_hash,
            data["gender"],
            data["college"],
            data["course"],
            data["year"],
            budget,
            data["preferred_location"]
        ))

        student_id = cursor.lastrowid

        connection.commit()

        return jsonify({
            "message": "Student registered successfully",
            "student_id": student_id
        }), 201

    except Exception as error:

        connection.rollback()

        return jsonify({
            "message": "Student registration failed",
            "error": str(error)
        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# STUDENT LOGIN
# =========================================================
@auth_bp.route("/student/login", methods=["POST"])
def student_login():

    data = request.get_json()

    if not data:

        return jsonify({
            "message": "Request body is required"
        }), 400

    if "email" not in data or "password" not in data:

        return jsonify({
            "message": "Email and password are required"
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                student_id,
                name,
                email,
                password_hash
            FROM student
            WHERE email = %s
        """, (data["email"],))

        student = cursor.fetchone()

    finally:

        cursor.close()
        connection.close()

    if not student:

        return jsonify({
            "message": "Invalid email or password"
        }), 401

    if not check_password_hash(
        student["password_hash"],
        data["password"]
    ):

        return jsonify({
            "message": "Invalid email or password"
        }), 401

    access_token = create_access_token(
        identity=str(student["student_id"]),
        additional_claims={
            "role": "student"
        }
    )

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "student": {
            "student_id": student["student_id"],
            "name": student["name"],
            "email": student["email"],
            "role": "student"
        }
    }), 200


# =========================================================
# HOSTEL OWNER LOGIN
# =========================================================
@auth_bp.route("/hostel-owner/login", methods=["POST"])
def hostel_owner_login():

    data = request.get_json()

    if not data:

        return jsonify({
            "message": "Request body is required"
        }), 400

    if "email" not in data or "password" not in data:

        return jsonify({
            "message": "Email and password are required"
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                hostel_owner_id,
                name,
                email,
                password_hash
            FROM hostel_owner
            WHERE email = %s
        """, (data["email"],))

        owner = cursor.fetchone()

    finally:

        cursor.close()
        connection.close()

    if not owner:

        return jsonify({
            "message": "Invalid email or password"
        }), 401

    if not check_password_hash(
        owner["password_hash"],
        data["password"]
    ):

        return jsonify({
            "message": "Invalid email or password"
        }), 401

    access_token = create_access_token(
        identity=str(owner["hostel_owner_id"]),
        additional_claims={
            "role": "hostel_owner"
        }
    )

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "hostel_owner_id": owner["hostel_owner_id"],
            "name": owner["name"],
            "email": owner["email"],
            "role": "hostel_owner"
        }
    }), 200


# =========================================================
# MESS OWNER LOGIN
# =========================================================
@auth_bp.route("/mess-owner/login", methods=["POST"])
def mess_owner_login():

    data = request.get_json()

    if not data:

        return jsonify({
            "message": "Request body is required"
        }), 400

    if "email" not in data or "password" not in data:

        return jsonify({
            "message": "Email and password are required"
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                mess_owner_id,
                name,
                email,
                password_hash
            FROM mess_owner
            WHERE email = %s
        """, (data["email"],))

        owner = cursor.fetchone()

    finally:

        cursor.close()
        connection.close()

    if not owner:

        return jsonify({
            "message": "Invalid email or password"
        }), 401

    if not check_password_hash(
        owner["password_hash"],
        data["password"]
    ):

        return jsonify({
            "message": "Invalid email or password"
        }), 401

    access_token = create_access_token(
        identity=str(owner["mess_owner_id"]),
        additional_claims={
            "role": "mess_owner"
        }
    )

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "mess_owner_id": owner["mess_owner_id"],
            "name": owner["name"],
            "email": owner["email"],
            "role": "mess_owner"
        }
    }), 200


# =========================================================
# ADMIN LOGIN
# =========================================================
@auth_bp.route("/admin/login", methods=["POST"])
def admin_login():

    data = request.get_json()

    if not data:

        return jsonify({
            "message": "Request body is required"
        }), 400

    if "email" not in data or "password" not in data:

        return jsonify({
            "message": "Email and password are required"
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                admin_id,
                name,
                email,
                password_hash
            FROM admin
            WHERE email = %s
        """, (data["email"],))

        admin = cursor.fetchone()

    finally:

        cursor.close()
        connection.close()

    if not admin:

        return jsonify({
            "message": "Invalid email or password"
        }), 401

    if not check_password_hash(
        admin["password_hash"],
        data["password"]
    ):

        return jsonify({
            "message": "Invalid email or password"
        }), 401

    access_token = create_access_token(
        identity=str(admin["admin_id"]),
        additional_claims={
            "role": "admin"
        }
    )

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": {
            "admin_id": admin["admin_id"],
            "name": admin["name"],
            "email": admin["email"],
            "role": "admin"
        }
    }), 200