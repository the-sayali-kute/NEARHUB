from flask import Blueprint, jsonify, request
from db import get_db_connection
from routes.auth_utils import hostel_owner_required
from flask_jwt_extended import get_jwt_identity

room_bp = Blueprint(
    "room",
    __name__,
    url_prefix="/api/rooms"
)


# GET all rooms
@room_bp.route("/", methods=["GET"])
def get_rooms():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            room_id,
            hostel_id,
            room_number,
            room_type,
            capacity,
            rent,
            available_beds,
            status
        FROM room
    """)

    rooms = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(rooms)


# GET room by ID
@room_bp.route("/<int:room_id>", methods=["GET"])
def get_room(room_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            room_id,
            hostel_id,
            room_number,
            room_type,
            capacity,
            rent,
            available_beds,
            status
        FROM room
        WHERE room_id = %s
    """, (room_id,))

    room = cursor.fetchone()

    cursor.close()
    connection.close()

    if room is None:
        return jsonify({
            "message": "Room not found"
        }), 404

    return jsonify(room)


# GET all rooms of a particular hostel
@room_bp.route("/hostel/<int:hostel_id>", methods=["GET"])
def get_hostel_rooms(hostel_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            room_id,
            hostel_id,
            room_number,
            room_type,
            capacity,
            rent,
            available_beds,
            status
        FROM room
        WHERE hostel_id = %s
    """, (hostel_id,))

    rooms = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(rooms)

# ADD ROOM
@room_bp.route("/", methods=["POST"])
@hostel_owner_required()
def add_room():

    data = request.get_json()

    required_fields = [
        "hostel_id",
        "room_number",
        "room_type",
        "capacity",
        "rent",
        "available_beds"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "message": f"{field} is required"
            }), 400

    if data["capacity"] <= 0:
        return jsonify({
            "message": "Capacity must be greater than 0"
        }), 400

    if data["available_beds"] < 0:
        return jsonify({
            "message": "Available beds cannot be negative"
        }), 400

    if data["available_beds"] > data["capacity"]:
        return jsonify({
            "message": "Available beds cannot be greater than capacity"
        }), 400


    owner_id = get_jwt_identity()

    connection = get_db_connection()
    cursor = connection.cursor()

    # Check whether hostel belongs to logged-in owner
    cursor.execute("""
        SELECT hostel_id
        FROM hostel
        WHERE hostel_id = %s
        AND hostel_owner_id = %s
    """, (data["hostel_id"], owner_id))

    hostel = cursor.fetchone()

    if hostel is None:
        cursor.close()
        connection.close()

        return jsonify({
            "message": "You can add rooms only to your own hostel"
        }), 403

    # Insert room
    cursor.execute("""
        INSERT INTO room
        (
            hostel_id,
            room_number,
            room_type,
            capacity,
            rent,
            available_beds,
            status
        )
        VALUES (%s, %s, %s, %s, %s, %s, 'Available')
    """, (
        data["hostel_id"],
        data["room_number"],
        data["room_type"],
        data["capacity"],
        data["rent"],
        data["available_beds"]
    ))

    connection.commit()

    new_room_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Room added successfully",
        "room_id": new_room_id,
        "status": "Available"
    }), 201

# UPDATE ROOM
@room_bp.route("/<int:room_id>", methods=["PUT"])
@hostel_owner_required()
def update_room(room_id):

    data = request.get_json()

    required_fields = [
        "room_number",
        "room_type",
        "capacity",
        "rent",
        "available_beds",
        "status"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "message": f"{field} is required"
            }), 400

    # Basic validation
    if data["capacity"] <= 0:
        return jsonify({
            "message": "Capacity must be greater than 0"
        }), 400

    if data["available_beds"] < 0:
        return jsonify({
            "message": "Available beds cannot be negative"
        }), 400

    if data["available_beds"] > data["capacity"]:
        return jsonify({
            "message": "Available beds cannot be greater than capacity"
        }), 400

    owner_id = get_jwt_identity()

    connection = get_db_connection()
    cursor = connection.cursor()

    # Check whether the room belongs to the logged-in owner's hostel
    cursor.execute("""
        SELECT r.room_id
        FROM room r
        JOIN hostel h
            ON r.hostel_id = h.hostel_id
        WHERE r.room_id = %s
        AND h.hostel_owner_id = %s
    """, (room_id, owner_id))

    room = cursor.fetchone()

    if room is None:
        cursor.close()
        connection.close()

        return jsonify({
            "message": "You can update only rooms in your own hostel"
        }), 403

    # Update room
    cursor.execute("""
        UPDATE room
        SET room_number = %s,
            room_type = %s,
            capacity = %s,
            rent = %s,
            available_beds = %s,
            status = %s
        WHERE room_id = %s
    """, (
        data["room_number"],
        data["room_type"],
        data["capacity"],
        data["rent"],
        data["available_beds"],
        data["status"],
        room_id
    ))

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Room updated successfully",
        "room_id": room_id
    }), 200

# DELETE ROOM
@room_bp.route("/<int:room_id>", methods=["DELETE"])
@hostel_owner_required()
def delete_room(room_id):

    owner_id = get_jwt_identity()

    connection = get_db_connection()
    cursor = connection.cursor()

    # Check whether the room belongs to the logged-in owner's hostel
    cursor.execute("""
        SELECT r.room_id
        FROM room r
        JOIN hostel h
            ON r.hostel_id = h.hostel_id
        WHERE r.room_id = %s
        AND h.hostel_owner_id = %s
    """, (room_id, owner_id))

    room = cursor.fetchone()

    if room is None:
        cursor.close()
        connection.close()

        return jsonify({
            "message": "You can delete only rooms in your own hostel"
        }), 403

    # Delete room
    cursor.execute("""
        DELETE FROM room
        WHERE room_id = %s
    """, (room_id,))

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Room deleted successfully",
        "room_id": room_id
    }), 200