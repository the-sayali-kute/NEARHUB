from flask import Blueprint, request
from db import get_db_connection
from routes.auth_utils import admin_required

admin_bp = Blueprint(
    "admin",
    __name__,
    url_prefix="/api/admin"
)


# ==============================
# GET PENDING HOSTELS
# ==============================
@admin_bp.route("/hostels/pending", methods=["GET"])
@admin_required()
def get_pending_hostels():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            h.hostel_id,
            h.hostel_name,
            h.location,
            h.address,
            h.description,
            h.contact_no,
            h.status,
            ho.name AS owner_name
        FROM hostel h
        JOIN hostel_owner ho
            ON h.hostel_owner_id = ho.hostel_owner_id
        WHERE h.status = 'Pending'
    """

    cursor.execute(query)
    hostels = cursor.fetchall()

    cursor.close()
    connection.close()

    return hostels, 200


# ==============================
# UPDATE HOSTEL STATUS
# ==============================
@admin_bp.route("/hostels/<int:hostel_id>/status", methods=["PUT"])
@admin_required()
def update_hostel_status(hostel_id):

    data = request.get_json()

    if "status" not in data:
        return {
            "message": "status is required"
        }, 400

    if data["status"] not in ["Approved", "Rejected"]:
        return {
            "message": "status must be Approved or Rejected"
        }, 400

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT hostel_id
        FROM hostel
        WHERE hostel_id = %s
        """,
        (hostel_id,)
    )

    hostel = cursor.fetchone()

    if not hostel:
        cursor.close()
        connection.close()

        return {
            "message": "Hostel not found"
        }, 404

    cursor.execute(
        """
        UPDATE hostel
        SET status = %s
        WHERE hostel_id = %s
        """,
        (data["status"], hostel_id)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "message": "Hostel status updated successfully"
    }, 200


# ==============================
# GET PENDING MESSES
# ==============================
@admin_bp.route("/messes/pending", methods=["GET"])
@admin_required()
def get_pending_messes():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            m.mess_id,
            m.mess_name,
            m.location,
            m.address,
            m.description,
            m.contact_no,
            m.food_type,
            m.status,
            CASE
                WHEN m.hostel_owner_id IS NOT NULL
                    THEN 'Hostel Owner'
                WHEN m.mess_owner_id IS NOT NULL
                    THEN 'Mess Owner'
            END AS owner_type
        FROM mess m
        WHERE m.status = 'Pending'
    """

    cursor.execute(query)
    messes = cursor.fetchall()

    cursor.close()
    connection.close()

    return messes, 200


# ==============================
# UPDATE MESS STATUS
# ==============================
@admin_bp.route("/messes/<int:mess_id>/status", methods=["PUT"])
@admin_required()
def update_mess_status(mess_id):

    data = request.get_json()

    if "status" not in data:
        return {
            "message": "status is required"
        }, 400

    if data["status"] not in ["Approved", "Rejected"]:
        return {
            "message": "status must be Approved or Rejected"
        }, 400

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT mess_id
        FROM mess
        WHERE mess_id = %s
        """,
        (mess_id,)
    )

    mess = cursor.fetchone()

    if not mess:
        cursor.close()
        connection.close()

        return {
            "message": "Mess not found"
        }, 404

    cursor.execute(
        """
        UPDATE mess
        SET status = %s
        WHERE mess_id = %s
        """,
        (data["status"], mess_id)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "message": "Mess status updated successfully"
    }, 200


# ==============================
# GET PENDING FEEDBACK
# ==============================
@admin_bp.route("/feedback/pending", methods=["GET"])
@admin_required()
def get_pending_feedback():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            f.feedback_id,
            f.student_id,
            s.name AS student_name,
            f.feedback_type,
            f.feedback_text,
            f.rating,
            f.hostel_id,
            h.hostel_name,
            f.mess_id,
            m.mess_name,
            f.status
        FROM feedback f
        JOIN student s
            ON f.student_id = s.student_id
        LEFT JOIN hostel h
            ON f.hostel_id = h.hostel_id
        LEFT JOIN mess m
            ON f.mess_id = m.mess_id
        WHERE f.status = 'Pending'
    """

    cursor.execute(query)
    feedback = cursor.fetchall()

    cursor.close()
    connection.close()

    return feedback, 200


# ==============================
# UPDATE FEEDBACK STATUS
# ==============================
@admin_bp.route("/feedback/<int:feedback_id>/status", methods=["PUT"])
@admin_required()
def update_feedback_status(feedback_id):

    data = request.get_json()

    if "status" not in data:
        return {
            "message": "status is required"
        }, 400

    if data["status"] not in ["Resolved", "Rejected"]:
        return {
            "message": "status must be Resolved or Rejected"
        }, 400

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT feedback_id
        FROM feedback
        WHERE feedback_id = %s
        """,
        (feedback_id,)
    )

    feedback = cursor.fetchone()

    if not feedback:
        cursor.close()
        connection.close()

        return {
            "message": "Feedback not found"
        }, 404

    cursor.execute(
        """
        UPDATE feedback
        SET status = %s
        WHERE feedback_id = %s
        """,
        (data["status"], feedback_id)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "message": "Feedback status updated successfully"
    }, 200


# ==============================
# ADMIN DASHBOARD
# ==============================
@admin_bp.route("/dashboard", methods=["GET"])
@admin_required()
def admin_dashboard():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    queries = {
        "students": "SELECT COUNT(*) AS count FROM student",
        "hostels": "SELECT COUNT(*) AS count FROM hostel",
        "messes": "SELECT COUNT(*) AS count FROM mess",
        "rooms": "SELECT COUNT(*) AS count FROM room",
        "bookings": "SELECT COUNT(*) AS count FROM room_booking",
        "subscriptions": "SELECT COUNT(*) AS count FROM meal_subscription",
        "feedback": "SELECT COUNT(*) AS count FROM feedback",
        "pending_hostels": """
            SELECT COUNT(*) AS count
            FROM hostel
            WHERE status = 'Pending'
        """,
        "pending_messes": """
            SELECT COUNT(*) AS count
            FROM mess
            WHERE status = 'Pending'
        """,
        "pending_feedback": """
            SELECT COUNT(*) AS count
            FROM feedback
            WHERE status = 'Pending'
        """
    }

    result = {}

    for key, query in queries.items():

        cursor.execute(query)
        row = cursor.fetchone()

        result[key] = row["count"]

    cursor.close()
    connection.close()

    return result, 200