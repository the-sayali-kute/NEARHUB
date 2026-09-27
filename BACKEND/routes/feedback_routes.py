from flask import Blueprint, jsonify, request
from db import get_db_connection
from routes.auth_utils import student_required
from flask_jwt_extended import get_jwt_identity


feedback_bp = Blueprint(
    "feedback",
    __name__,
    url_prefix="/api/feedback"
)


# =========================================================
# GET ALL FEEDBACK
# =========================================================
# Public endpoint
# Used mainly for testing/admin-related viewing.
# For the final frontend, you may make this admin-only.
@feedback_bp.route("/", methods=["GET"])
def get_feedback():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            f.feedback_id,
            f.hostel_id,
            h.hostel_name,
            f.mess_id,
            m.mess_name,
            f.rating,
            f.feedback_text,
            f.feedback_type,
            f.feedback_date,
            f.status
        FROM feedback f
        LEFT JOIN hostel h
            ON f.hostel_id = h.hostel_id
        LEFT JOIN mess m
            ON f.mess_id = m.mess_id
        ORDER BY f.feedback_id DESC
    """)

    feedback = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(feedback)


# =========================================================
# GET SINGLE FEEDBACK
# =========================================================
# Student can view only their own feedback.
@feedback_bp.route("/<int:feedback_id>", methods=["GET"])
@student_required()
def get_feedback_by_id(feedback_id):

    student_id = int(get_jwt_identity())

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            f.feedback_id,
            f.student_id,
            f.hostel_id,
            h.hostel_name,
            f.mess_id,
            m.mess_name,
            f.rating,
            f.feedback_text,
            f.feedback_type,
            f.feedback_date,
            f.status
        FROM feedback f
        LEFT JOIN hostel h
            ON f.hostel_id = h.hostel_id
        LEFT JOIN mess m
            ON f.mess_id = m.mess_id
        WHERE f.feedback_id = %s
          AND f.student_id = %s
    """, (feedback_id, student_id))

    feedback = cursor.fetchone()

    cursor.close()
    connection.close()

    if feedback is None:
        return jsonify({
            "message": "Feedback not found"
        }), 404

    return jsonify(feedback)


# =========================================================
# GET MY FEEDBACK
# =========================================================
@feedback_bp.route("/my", methods=["GET"])
@student_required()
def get_my_feedback():

    student_id = int(get_jwt_identity())

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            f.feedback_id,
            f.hostel_id,
            h.hostel_name,
            f.mess_id,
            m.mess_name,
            f.rating,
            f.feedback_text,
            f.feedback_type,
            f.feedback_date,
            f.status
        FROM feedback f
        LEFT JOIN hostel h
            ON f.hostel_id = h.hostel_id
        LEFT JOIN mess m
            ON f.mess_id = m.mess_id
        WHERE f.student_id = %s
        ORDER BY f.feedback_id DESC
    """, (student_id,))

    feedback = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(feedback)


# =========================================================
# CREATE FEEDBACK
# =========================================================
@feedback_bp.route("/", methods=["POST"])
@student_required()
def create_feedback():

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
        "feedback_type",
        "feedback_text"
    ]

    for field in required_fields:

        if field not in data:
            return jsonify({
                "message": f"{field} is required"
            }), 400

    feedback_type = data["feedback_type"]
    feedback_text = data["feedback_text"]

    # -----------------------------------------------------
    # VALIDATE FEEDBACK TYPE
    # -----------------------------------------------------
    if feedback_type not in ["Review", "Complaint"]:

        return jsonify({
            "message": "feedback_type must be Review or Complaint"
        }), 400

    # -----------------------------------------------------
    # VALIDATE FEEDBACK TEXT
    # -----------------------------------------------------
    if not isinstance(feedback_text, str) or not feedback_text.strip():

        return jsonify({
            "message": "feedback_text cannot be empty"
        }), 400

    feedback_text = feedback_text.strip()

    # -----------------------------------------------------
    # GET TARGET
    # -----------------------------------------------------
    hostel_id = data.get("hostel_id")
    mess_id = data.get("mess_id")
    rating = data.get("rating")

    # -----------------------------------------------------
    # EXACTLY ONE TARGET REQUIRED
    # -----------------------------------------------------
    if (
        (hostel_id is None and mess_id is None)
        or
        (hostel_id is not None and mess_id is not None)
    ):

        return jsonify({
            "message": "Feedback must belong to either a hostel or a mess, not both"
        }), 400

    # -----------------------------------------------------
    # VALIDATE REVIEW
    # -----------------------------------------------------
    if feedback_type == "Review":

        if rating is None:

            return jsonify({
                "message": "Rating is required for a review"
            }), 400

        # bool is technically an int in Python,
        # so explicitly reject True/False.
        if isinstance(rating, bool) or not isinstance(rating, int):

            return jsonify({
                "message": "Rating must be an integer between 1 and 5"
            }), 400

        if rating < 1 or rating > 5:

            return jsonify({
                "message": "Rating must be between 1 and 5"
            }), 400

    # -----------------------------------------------------
    # VALIDATE COMPLAINT
    # -----------------------------------------------------
    if feedback_type == "Complaint":

        if rating is not None:

            return jsonify({
                "message": "Complaint cannot have a rating"
            }), 400

        rating = None

    # -----------------------------------------------------
    # DATABASE CONNECTION
    # -----------------------------------------------------
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        # =================================================
        # CHECK STUDENT
        # =================================================
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

        # =================================================
        # CHECK HOSTEL
        # =================================================
        if hostel_id is not None:

            cursor.execute("""
                SELECT
                    hostel_id,
                    hostel_name,
                    status
                FROM hostel
                WHERE hostel_id = %s
            """, (hostel_id,))

            hostel = cursor.fetchone()

            if hostel is None:

                return jsonify({
                    "message": "Hostel not found"
                }), 404

            if hostel["status"] != "Approved":

                return jsonify({
                    "message": "Feedback can be submitted only for an approved hostel"
                }), 400

        # =================================================
        # CHECK MESS
        # =================================================
        if mess_id is not None:

            cursor.execute("""
                SELECT
                    mess_id,
                    mess_name,
                    status
                FROM mess
                WHERE mess_id = %s
            """, (mess_id,))

            mess = cursor.fetchone()

            if mess is None:

                return jsonify({
                    "message": "Mess not found"
                }), 404

            if mess["status"] != "Approved":

                return jsonify({
                    "message": "Feedback can be submitted only for an approved mess"
                }), 400

        # =================================================
        # INSERT FEEDBACK
        # =================================================
        cursor.execute("""
            INSERT INTO feedback
            (
                student_id,
                hostel_id,
                mess_id,
                rating,
                feedback_text,
                feedback_type,
                status
            )
            VALUES
            (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                'Pending'
            )
        """, (
            student_id,
            hostel_id,
            mess_id,
            rating,
            feedback_text,
            feedback_type
        ))

        feedback_id = cursor.lastrowid

        connection.commit()

        return jsonify({
            "message": "Feedback submitted successfully",
            "feedback_id": feedback_id,
            "feedback_type": feedback_type,
            "status": "Pending"
        }), 201

    except Exception as error:

        connection.rollback()

        return jsonify({
            "message": "Feedback submission failed",
            "error": str(error)
        }), 500

    finally:

        cursor.close()
        connection.close()