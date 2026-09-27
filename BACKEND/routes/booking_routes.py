from datetime import datetime

from flask import Blueprint, jsonify, request
from db import get_db_connection
from routes.auth_utils import student_required
from flask_jwt_extended import (
    get_jwt_identity,
    get_jwt,
    verify_jwt_in_request
)


booking_bp = Blueprint(
    "booking",
    __name__,
    url_prefix="/api/bookings"
)


# =========================================================
# GET ALL BOOKINGS
# ADMIN ONLY
# =========================================================
@booking_bp.route("/", methods=["GET"])
def get_bookings():

    # Verify JWT
    verify_jwt_in_request()

    claims = get_jwt()

    # Only admin can view all bookings
    if claims.get("role") != "admin":
        return jsonify({
            "message": "Admin access required"
        }), 403

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                rb.booking_id,
                rb.student_id,
                s.name AS student_name,
                rb.room_id,
                r.room_number,
                r.room_type,
                r.rent,
                h.hostel_id,
                h.hostel_name,
                rb.booking_date,
                rb.start_date,
                rb.end_date,
                rb.status
            FROM room_booking rb
            JOIN student s
                ON rb.student_id = s.student_id
            JOIN room r
                ON rb.room_id = r.room_id
            JOIN hostel h
                ON r.hostel_id = h.hostel_id
            ORDER BY rb.booking_id DESC
        """)

        bookings = cursor.fetchall()

        return jsonify(bookings), 200

    finally:

        cursor.close()
        connection.close()


# =========================================================
# GET SINGLE BOOKING
# STUDENT CAN VIEW ONLY OWN BOOKING
# =========================================================
@booking_bp.route("/<int:booking_id>", methods=["GET"])
@student_required()
def get_booking(booking_id):

    student_id = int(get_jwt_identity())

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                rb.booking_id,
                rb.student_id,
                s.name AS student_name,
                rb.room_id,
                r.room_number,
                r.room_type,
                r.rent,
                h.hostel_id,
                h.hostel_name,
                rb.booking_date,
                rb.start_date,
                rb.end_date,
                rb.status
            FROM room_booking rb
            JOIN student s
                ON rb.student_id = s.student_id
            JOIN room r
                ON rb.room_id = r.room_id
            JOIN hostel h
                ON r.hostel_id = h.hostel_id
            WHERE rb.booking_id = %s
              AND rb.student_id = %s
        """, (booking_id, student_id))

        booking = cursor.fetchone()

        if booking is None:
            return jsonify({
                "message": "Booking not found"
            }), 404

        return jsonify(booking), 200

    finally:

        cursor.close()
        connection.close()


# =========================================================
# GET MY BOOKINGS
# STUDENT ONLY
# =========================================================
@booking_bp.route("/my", methods=["GET"])
@student_required()
def get_my_bookings():

    student_id = int(get_jwt_identity())

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                rb.booking_id,
                rb.student_id,
                rb.room_id,
                r.room_number,
                r.room_type,
                r.rent,
                h.hostel_id,
                h.hostel_name,
                h.location,
                rb.booking_date,
                rb.start_date,
                rb.end_date,
                rb.status
            FROM room_booking rb
            JOIN room r
                ON rb.room_id = r.room_id
            JOIN hostel h
                ON r.hostel_id = h.hostel_id
            WHERE rb.student_id = %s
            ORDER BY rb.booking_id DESC
        """, (student_id,))

        bookings = cursor.fetchall()

        return jsonify(bookings), 200

    finally:

        cursor.close()
        connection.close()


# =========================================================
# CREATE BOOKING
# STUDENT ONLY
# =========================================================
@booking_bp.route("/", methods=["POST"])
@student_required()
def create_booking():

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
        "room_id",
        "start_date",
        "end_date"
    ]

    for field in required_fields:

        if field not in data:
            return jsonify({
                "message": f"{field} is required"
            }), 400

    # -----------------------------------------------------
    # VALIDATE ROOM ID
    # -----------------------------------------------------
    try:
        room_id = int(data["room_id"])

    except (TypeError, ValueError):

        return jsonify({
            "message": "room_id must be a valid integer"
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
        # LOCK ROOM
        # -------------------------------------------------
        cursor.execute("""
            SELECT
                room_id,
                hostel_id,
                room_number,
                room_type,
                available_beds,
                capacity,
                status
            FROM room
            WHERE room_id = %s
            FOR UPDATE
        """, (room_id,))

        room = cursor.fetchone()

        if room is None:

            return jsonify({
                "message": "Room not found"
            }), 404

        # -------------------------------------------------
        # CHECK ROOM STATUS
        # -------------------------------------------------
        if room["status"] != "Available":

            return jsonify({
                "message": "Room is not available"
            }), 400

        # -------------------------------------------------
        # CHECK AVAILABLE BEDS
        # -------------------------------------------------
        if room["available_beds"] <= 0:

            return jsonify({
                "message": "No beds available"
            }), 400

        # -------------------------------------------------
        # CHECK HOSTEL APPROVAL
        # -------------------------------------------------
        cursor.execute("""
            SELECT
                hostel_id,
                status
            FROM hostel
            WHERE hostel_id = %s
        """, (room["hostel_id"],))

        hostel = cursor.fetchone()

        if hostel is None:

            return jsonify({
                "message": "Hostel not found"
            }), 404

        if hostel["status"] != "Approved":

            return jsonify({
                "message": "Booking is allowed only in an approved hostel"
            }), 400

        # -------------------------------------------------
        # CHECK EXISTING ACTIVE BOOKING
        # -------------------------------------------------
        cursor.execute("""
            SELECT booking_id
            FROM room_booking
            WHERE student_id = %s
              AND status IN ('Pending', 'Confirmed')
            LIMIT 1
        """, (student_id,))

        existing_booking = cursor.fetchone()

        if existing_booking is not None:

            return jsonify({
                "message": "You already have an active room booking"
            }), 400

        # -------------------------------------------------
        # CREATE BOOKING
        # -------------------------------------------------
        cursor.execute("""
            INSERT INTO room_booking
            (
                student_id,
                room_id,
                booking_date,
                start_date,
                end_date,
                status
            )
            VALUES
            (
                %s,
                %s,
                NOW(),
                %s,
                %s,
                'Pending'
            )
        """, (
            student_id,
            room_id,
            start_date,
            end_date
        ))

        booking_id = cursor.lastrowid


       

        connection.commit()

        return jsonify({
            "message": "Room booking created successfully",
            "booking_id": booking_id,
            "status": "Pending"
        }), 201

    except Exception as error:

        connection.rollback()

        return jsonify({
            "message": "Booking failed",
            "error": str(error)
        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# CANCEL MY BOOKING
# STUDENT ONLY
# =========================================================
@booking_bp.route("/<int:booking_id>/cancel", methods=["PUT"])
@student_required()
def cancel_booking(booking_id):

    student_id = int(get_jwt_identity())

    connection = get_db_connection()

    try:

        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # LOCK BOOKING
        # -------------------------------------------------
        cursor.execute("""
            SELECT
                booking_id,
                room_id,
                status
            FROM room_booking
            WHERE booking_id = %s
              AND student_id = %s
            FOR UPDATE
        """, (booking_id, student_id))

        booking = cursor.fetchone()

        if booking is None:

            return jsonify({
                "message": "Booking not found"
            }), 404

        # -------------------------------------------------
        # ALREADY CANCELLED
        # -------------------------------------------------
        if booking["status"] == "Cancelled":

            return jsonify({
                "message": "Booking is already cancelled"
            }), 400

        # -------------------------------------------------
        # COMPLETED BOOKING
        # -------------------------------------------------
        if booking["status"] == "Completed":

            return jsonify({
                "message": "Completed booking cannot be cancelled"
            }), 400

        # -------------------------------------------------
        # CANCEL BOOKING
        # -------------------------------------------------
        cursor.execute("""
            UPDATE room_booking
            SET status = 'Cancelled'
            WHERE booking_id = %s
        """, (booking_id,))

        # -------------------------------------------------
        # RESTORE BED
        # -------------------------------------------------
        

        connection.commit()

        return jsonify({
            "message": "Booking cancelled successfully",
            "booking_id": booking_id,
            "status": "Cancelled"
        }), 200

    except Exception as error:

        connection.rollback()

        return jsonify({
            "message": "Failed to cancel booking",
            "error": str(error)
        }), 500

    finally:

        cursor.close()
        connection.close()


# =========================================================
# UPDATE BOOKING STATUS
# HOSTEL OWNER / ADMIN
# =========================================================
@booking_bp.route("/<int:booking_id>/status", methods=["PUT"])
def update_booking_status(booking_id):

    # -----------------------------------------------------
    # VERIFY JWT
    # -----------------------------------------------------
    verify_jwt_in_request()

    claims = get_jwt()

    role = claims.get("role")
    user_id = int(get_jwt_identity())

    # -----------------------------------------------------
    # CHECK ROLE
    # -----------------------------------------------------
    if role not in ["admin", "hostel_owner"]:

        return jsonify({
            "message": "Only hostel owners and admins can update booking status"
        }), 403

    data = request.get_json()

    if not data:

        return jsonify({
            "message": "Request body is required"
        }), 400

    if "status" not in data:

        return jsonify({
            "message": "status is required"
        }), 400

    new_status = data["status"]

    if new_status not in ["Confirmed", "Cancelled"]:

        return jsonify({
            "message": "Status must be Confirmed or Cancelled"
        }), 400

    connection = get_db_connection()

    try:

        cursor = connection.cursor(dictionary=True)

        # =================================================
        # ADMIN
        # =================================================
        if role == "admin":

            cursor.execute("""
                SELECT
                    rb.booking_id,
                    rb.room_id,
                    rb.status,
                    r.available_beds,
                    r.capacity
                FROM room_booking rb
                JOIN room r
                    ON rb.room_id = r.room_id
                WHERE rb.booking_id = %s
                FOR UPDATE
            """, (booking_id,))

        # =================================================
        # HOSTEL OWNER
        # =================================================
        else:

            cursor.execute("""
                SELECT
                    rb.booking_id,
                    rb.room_id,
                    rb.status,
                    r.available_beds,
                    r.capacity
                FROM room_booking rb
                JOIN room r
                    ON rb.room_id = r.room_id
                JOIN hostel h
                    ON r.hostel_id = h.hostel_id
                WHERE rb.booking_id = %s
                  AND h.hostel_owner_id = %s
                FOR UPDATE
            """, (booking_id, user_id))

        booking = cursor.fetchone()

        if booking is None:

            return jsonify({
                "message": "Booking not found or access denied"
            }), 404

        # -------------------------------------------------
        # ONLY PENDING CAN BE UPDATED
        # -------------------------------------------------
        if booking["status"] != "Pending":

            return jsonify({
                "message": "Only pending bookings can be updated"
            }), 400

        # -------------------------------------------------
        # CONFIRM BOOKING
        # -------------------------------------------------
        if new_status == "Confirmed":

            cursor.execute("""
                UPDATE room_booking
                SET status = 'Confirmed'
                WHERE booking_id = %s
            """, (booking_id,))

        # -------------------------------------------------
        # CANCEL BOOKING
        # -------------------------------------------------
        elif new_status == "Cancelled":

            cursor.execute("""
                UPDATE room_booking
                SET status = 'Cancelled'
                WHERE booking_id = %s
            """, (booking_id,))



        connection.commit()

        return jsonify({
            "message": f"Booking {new_status.lower()} successfully",
            "booking_id": booking_id,
            "status": new_status
        }), 200

    except Exception as error:

        connection.rollback()

        return jsonify({
            "message": "Failed to update booking",
            "error": str(error)
        }), 500

    finally:

        cursor.close()
        connection.close()