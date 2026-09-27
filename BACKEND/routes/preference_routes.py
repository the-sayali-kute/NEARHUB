from flask import Blueprint, jsonify, request
from db import get_db_connection
from routes.auth_utils import student_required, admin_required
from flask_jwt_extended import get_jwt_identity


preference_bp = Blueprint(
    "preference",
    __name__,
    url_prefix="/api/preferences"
)


# =========================================================
# GET ALL STUDENT PREFERENCES
# ADMIN ONLY
# =========================================================
@preference_bp.route("/", methods=["GET"])
@admin_required()
def get_all_preferences():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                sp.preference_id,
                sp.student_id,
                s.name AS student_name,
                sp.preferred_location,
                sp.max_budget,
                sp.room_type,
                sp.food_type,
                sp.meal_preference,
                sp.required_facility
            FROM student_preference sp
            JOIN student s
                ON sp.student_id = s.student_id
            ORDER BY sp.preference_id
        """)

        preferences = cursor.fetchall()

        return jsonify(preferences), 200

    finally:

        cursor.close()
        connection.close()


# =========================================================
# GET MY PREFERENCE
# STUDENT ONLY
# =========================================================
@preference_bp.route("/my", methods=["GET"])
@student_required()
def get_my_preference():

    student_id = int(get_jwt_identity())

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                sp.preference_id,
                sp.student_id,
                sp.preferred_location,
                sp.max_budget,
                sp.room_type,
                sp.food_type,
                sp.meal_preference,
                sp.required_facility
            FROM student_preference sp
            WHERE sp.student_id = %s
        """, (student_id,))

        preference = cursor.fetchone()

        if preference is None:
            return jsonify({
                "message": "Preference not found"
            }), 404

        return jsonify(preference), 200

    finally:

        cursor.close()
        connection.close()


# =========================================================
# ADD MY PREFERENCE
# STUDENT ONLY
# =========================================================
@preference_bp.route("/", methods=["POST"])
@student_required()
def add_preference():

    student_id = int(get_jwt_identity())

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "Request body is required"
        }), 400

    # -----------------------------------------------------
    # REQUIRED FIELDS
    # -----------------------------------------------------
    required_fields = [
        "preferred_location",
        "max_budget",
        "room_type",
        "food_type",
        "meal_preference",
        "required_facility"
    ]

    for field in required_fields:

        if field not in data:
            return jsonify({
                "message": f"{field} is required"
            }), 400

    # -----------------------------------------------------
    # VALIDATE MAX BUDGET
    # -----------------------------------------------------
    try:
        max_budget = float(data["max_budget"])

    except (TypeError, ValueError):

        return jsonify({
            "message": "max_budget must be a number"
        }), 400

    if max_budget < 0:

        return jsonify({
            "message": "max_budget cannot be negative"
        }), 400

    # -----------------------------------------------------
    # DATABASE CONNECTION
    # -----------------------------------------------------
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        # -------------------------------------------------
        # CHECK STUDENT EXISTS
        # -------------------------------------------------
        cursor.execute("""
            SELECT student_id
            FROM student
            WHERE student_id = %s
        """, (student_id,))

        student = cursor.fetchone()

        if student is None:

            return jsonify({
                "message": "Student not found"
            }), 404

        # -------------------------------------------------
        # CHECK WHETHER PREFERENCE ALREADY EXISTS
        # -------------------------------------------------
        cursor.execute("""
            SELECT preference_id
            FROM student_preference
            WHERE student_id = %s
        """, (student_id,))

        existing = cursor.fetchone()

        if existing:

            return jsonify({
                "message": "Preference already exists for this student. Use PUT /api/preferences/my to update it."
            }), 400

        # -------------------------------------------------
        # INSERT PREFERENCE
        # -------------------------------------------------
        cursor.execute("""
            INSERT INTO student_preference
            (
                student_id,
                preferred_location,
                max_budget,
                room_type,
                food_type,
                meal_preference,
                required_facility
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
        """, (
            student_id,
            data["preferred_location"],
            max_budget,
            data["room_type"],
            data["food_type"],
            data["meal_preference"],
            data["required_facility"]
        ))

        preference_id = cursor.lastrowid

        connection.commit()

        return jsonify({
            "message": "Student preference added successfully",
            "preference_id": preference_id
        }), 201

    except Exception as error:

        connection.rollback()

        return jsonify({
            "message": "Failed to add student preference",
            "error": str(error)
        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# UPDATE MY PREFERENCE
# STUDENT ONLY
# =========================================================
@preference_bp.route("/my", methods=["PUT"])
@student_required()
def update_my_preference():

    student_id = int(get_jwt_identity())

    data = request.get_json()

    if not data:

        return jsonify({
            "message": "Request body is required"
        }), 400

    # -----------------------------------------------------
    # REQUIRED FIELDS
    # -----------------------------------------------------
    required_fields = [
        "preferred_location",
        "max_budget",
        "room_type",
        "food_type",
        "meal_preference",
        "required_facility"
    ]

    for field in required_fields:

        if field not in data:

            return jsonify({
                "message": f"{field} is required"
            }), 400

    # -----------------------------------------------------
    # VALIDATE MAX BUDGET
    # -----------------------------------------------------
    try:

        max_budget = float(data["max_budget"])

    except (TypeError, ValueError):

        return jsonify({
            "message": "max_budget must be a number"
        }), 400

    if max_budget < 0:

        return jsonify({
            "message": "max_budget cannot be negative"
        }), 400

    # -----------------------------------------------------
    # DATABASE CONNECTION
    # -----------------------------------------------------
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        # -------------------------------------------------
        # CHECK PREFERENCE EXISTS
        # -------------------------------------------------
        cursor.execute("""
            SELECT preference_id
            FROM student_preference
            WHERE student_id = %s
        """, (student_id,))

        preference = cursor.fetchone()

        if preference is None:

            return jsonify({
                "message": "Preference not found. Create your preference first."
            }), 404

        # -------------------------------------------------
        # UPDATE PREFERENCE
        # -------------------------------------------------
        cursor.execute("""
            UPDATE student_preference
            SET
                preferred_location = %s,
                max_budget = %s,
                room_type = %s,
                food_type = %s,
                meal_preference = %s,
                required_facility = %s
            WHERE student_id = %s
        """, (
            data["preferred_location"],
            max_budget,
            data["room_type"],
            data["food_type"],
            data["meal_preference"],
            data["required_facility"],
            student_id
        ))

        connection.commit()

        return jsonify({
            "message": "Student preference updated successfully"
        }), 200

    except Exception as error:

        connection.rollback()

        return jsonify({
            "message": "Failed to update student preference",
            "error": str(error)
        }), 500

    finally:

        cursor.close()
        connection.close()