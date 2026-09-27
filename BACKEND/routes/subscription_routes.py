from datetime import datetime

from flask import Blueprint, jsonify, request
from db import get_db_connection
from routes.auth_utils import student_required
from flask_jwt_extended import (
    get_jwt_identity,
    get_jwt,
    verify_jwt_in_request
)


subscription_bp = Blueprint(
    "subscription",
    __name__,
    url_prefix="/api/subscriptions"
)


# =========================================================
# GET ALL SUBSCRIPTIONS
# ADMIN ONLY
# =========================================================
@subscription_bp.route("/", methods=["GET"])
def get_subscriptions():

    # Verify JWT
    verify_jwt_in_request()

    claims = get_jwt()

    # Only admin can see all student subscriptions
    if claims.get("role") != "admin":
        return jsonify({
            "message": "Admin access required"
        }), 403

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                ms.subscription_id,
                ms.student_id,
                s.name AS student_name,
                ms.plan_id,
                mp.plan_name,
                mp.price,
                mp.meals_per_day,
                mp.duration,
                m.mess_id,
                m.mess_name,
                ms.start_date,
                ms.end_date,
                ms.status
            FROM meal_subscription ms
            JOIN student s
                ON ms.student_id = s.student_id
            JOIN meal_plan mp
                ON ms.plan_id = mp.plan_id
            JOIN mess m
                ON mp.mess_id = m.mess_id
            ORDER BY ms.subscription_id DESC
        """)

        subscriptions = cursor.fetchall()

        return jsonify(subscriptions), 200

    finally:

        cursor.close()
        connection.close()


# =========================================================
# GET MY SUBSCRIPTIONS
# STUDENT ONLY
# =========================================================
@subscription_bp.route("/my", methods=["GET"])
@student_required()
def get_my_subscriptions():

    student_id = int(get_jwt_identity())

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                ms.subscription_id,
                ms.plan_id,
                mp.plan_name,
                mp.price,
                mp.meals_per_day,
                mp.duration,
                m.mess_id,
                m.mess_name,
                ms.start_date,
                ms.end_date,
                ms.status
            FROM meal_subscription ms
            JOIN meal_plan mp
                ON ms.plan_id = mp.plan_id
            JOIN mess m
                ON mp.mess_id = m.mess_id
            WHERE ms.student_id = %s
            ORDER BY ms.subscription_id DESC
        """, (student_id,))

        subscriptions = cursor.fetchall()

        return jsonify(subscriptions), 200

    finally:

        cursor.close()
        connection.close()


# =========================================================
# GET SUBSCRIPTION BY ID
# STUDENT CAN VIEW ONLY THEIR OWN
# =========================================================
@subscription_bp.route("/<int:subscription_id>", methods=["GET"])
@student_required()
def get_subscription(subscription_id):

    student_id = int(get_jwt_identity())

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                ms.subscription_id,
                ms.student_id,
                s.name AS student_name,
                ms.plan_id,
                mp.plan_name,
                mp.price,
                mp.meals_per_day,
                mp.duration,
                m.mess_id,
                m.mess_name,
                ms.start_date,
                ms.end_date,
                ms.status
            FROM meal_subscription ms
            JOIN student s
                ON ms.student_id = s.student_id
            JOIN meal_plan mp
                ON ms.plan_id = mp.plan_id
            JOIN mess m
                ON mp.mess_id = m.mess_id
            WHERE ms.subscription_id = %s
              AND ms.student_id = %s
        """, (subscription_id, student_id))

        subscription = cursor.fetchone()

        if subscription is None:

            return jsonify({
                "message": "Subscription not found"
            }), 404

        return jsonify(subscription), 200

    finally:

        cursor.close()
        connection.close()


# =========================================================
# CREATE MEAL SUBSCRIPTION
# STUDENT ONLY
# =========================================================
@subscription_bp.route("/", methods=["POST"])
@student_required()
def create_subscription():

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
        "plan_id",
        "start_date",
        "end_date"
    ]

    for field in required_fields:

        if field not in data:

            return jsonify({
                "message": f"{field} is required"
            }), 400

    # -----------------------------------------------------
    # VALIDATE PLAN ID
    # -----------------------------------------------------
    try:

        plan_id = int(data["plan_id"])

    except (TypeError, ValueError):

        return jsonify({
            "message": "plan_id must be a valid integer"
        }), 400

    # -----------------------------------------------------
    # VALIDATE DATES
    # -----------------------------------------------------
    try:

        start_date = datetime.strptime(
            data["start_date"],
            "%Y-%m-%d"
        ).date()

        end_date = datetime.strptime(
            data["end_date"],
            "%Y-%m-%d"
        ).date()

    except (TypeError, ValueError):

        return jsonify({
            "message": "Dates must be in YYYY-MM-DD format"
        }), 400

    if end_date <= start_date:

        return jsonify({
            "message": "End date must be after start date"
        }), 400

    # -----------------------------------------------------
    # DATABASE CONNECTION
    # -----------------------------------------------------
    connection = get_db_connection()

    try:

        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # CHECK STUDENT
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
        # CHECK MEAL PLAN + APPROVED MESS
        # -------------------------------------------------
        cursor.execute("""
            SELECT
                mp.plan_id,
                mp.plan_name,
                mp.price,
                mp.meals_per_day,
                mp.duration,
                m.mess_id,
                m.mess_name,
                m.status
            FROM meal_plan mp
            JOIN mess m
                ON mp.mess_id = m.mess_id
            WHERE mp.plan_id = %s
              AND m.status = 'Approved'
        """, (plan_id,))

        plan = cursor.fetchone()

        if plan is None:

            return jsonify({
                "message": "Meal plan not found or its mess is not approved"
            }), 404

        # -------------------------------------------------
        # CHECK ACTIVE SUBSCRIPTION
        # -------------------------------------------------
        cursor.execute("""
            SELECT
                subscription_id,
                status
            FROM meal_subscription
            WHERE student_id = %s
              AND status = 'Active'
            FOR UPDATE
        """, (student_id,))

        existing_subscription = cursor.fetchone()

        if existing_subscription is not None:

            return jsonify({
                "message": "You already have an active meal subscription"
            }), 400

        # -------------------------------------------------
        # CREATE SUBSCRIPTION
        # -------------------------------------------------
        cursor.execute("""
            INSERT INTO meal_subscription
            (
                student_id,
                plan_id,
                start_date,
                end_date,
                status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                'Active'
            )
        """, (
            student_id,
            plan_id,
            start_date,
            end_date
        ))

        subscription_id = cursor.lastrowid

        connection.commit()

        return jsonify({
            "message": "Meal subscription created successfully",
            "subscription_id": subscription_id,
            "status": "Active"
        }), 201

    except Exception as error:

        connection.rollback()

        return jsonify({
            "message": "Subscription failed",
            "error": str(error)
        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# CANCEL MEAL SUBSCRIPTION
# STUDENT ONLY
# =========================================================
@subscription_bp.route(
    "/<int:subscription_id>/cancel",
    methods=["PUT"]
)
@student_required()
def cancel_subscription(subscription_id):

    student_id = int(get_jwt_identity())

    connection = get_db_connection()

    try:

        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # FIND ONLY LOGGED-IN STUDENT'S SUBSCRIPTION
        # -------------------------------------------------
        cursor.execute("""
            SELECT
                subscription_id,
                status
            FROM meal_subscription
            WHERE subscription_id = %s
              AND student_id = %s
            FOR UPDATE
        """, (subscription_id, student_id))

        subscription = cursor.fetchone()

        if subscription is None:

            return jsonify({
                "message": "Subscription not found"
            }), 404

        # -------------------------------------------------
        # ALREADY CANCELLED
        # -------------------------------------------------
        if subscription["status"] == "Cancelled":

            return jsonify({
                "message": "Subscription is already cancelled"
            }), 400

        # -------------------------------------------------
        # EXPIRED
        # -------------------------------------------------
        if subscription["status"] == "Expired":

            return jsonify({
                "message": "Expired subscription cannot be cancelled"
            }), 400

        # -------------------------------------------------
        # CANCEL SUBSCRIPTION
        # -------------------------------------------------
        cursor.execute("""
            UPDATE meal_subscription
            SET status = 'Cancelled'
            WHERE subscription_id = %s
              AND student_id = %s
        """, (subscription_id, student_id))

        connection.commit()

        return jsonify({
            "message": "Meal subscription cancelled successfully",
            "subscription_id": subscription_id,
            "status": "Cancelled"
        }), 200

    except Exception as error:

        connection.rollback()

        return jsonify({
            "message": "Failed to cancel subscription",
            "error": str(error)
        }), 500

    finally:

        cursor.close()
        connection.close()