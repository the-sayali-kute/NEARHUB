from flask import Blueprint, jsonify, request
from db import get_db_connection
from routes.auth_utils import hostel_owner_required
from flask_jwt_extended import get_jwt_identity


hostel_bp = Blueprint(
    "hostel",
    __name__,
    url_prefix="/api/hostels"
)


@hostel_bp.route("/", methods=["GET"])
def get_hostels():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            h.hostel_id,
            h.hostel_name,
            h.address,
            h.location,
            h.description,
            h.gender_type,
            h.contact_no,
            h.status,
            ho.name AS owner_name
            FROM hostel h
            JOIN hostel_owner ho
                ON h.hostel_owner_id = ho.hostel_owner_id
            WHERE h.status = 'Approved'
    """)

    hostels = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(hostels)


@hostel_bp.route("/<int:hostel_id>", methods=["GET"])
def get_hostel(hostel_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            h.hostel_id,
            h.hostel_name,
            h.address,
            h.location,
            h.description,
            h.gender_type,
            h.contact_no,
            h.status,
            ho.name AS owner_name
        FROM hostel h
        JOIN hostel_owner ho
            ON h.hostel_owner_id = ho.hostel_owner_id
        WHERE h.hostel_id = %s
        AND h.status = 'Approved'
    """, (hostel_id,))

    hostel = cursor.fetchone()

    cursor.close()
    connection.close()

    if hostel is None:
        return jsonify({
            "message": "Hostel not found"
        }), 404

    return jsonify(hostel)

# =====================================
# HOSTEL OWNER - MY HOSTELS
# =====================================

@hostel_bp.route("/owner/my-hostels", methods=["GET"])
@hostel_owner_required()
def get_my_hostels():

    owner_id = get_jwt_identity()

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            h.hostel_id,
            h.hostel_name,
            h.address,
            h.location,
            h.description,
            h.gender_type,
            h.contact_no,
            h.status,
            ho.name AS owner_name
        FROM hostel h
        JOIN hostel_owner ho
            ON h.hostel_owner_id = ho.hostel_owner_id
        WHERE h.hostel_owner_id = %s
    """, (owner_id,))

    hostels = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(hostels)

# =====================================
# HOSTEL OWNER - CREATE HOSTEL
# =====================================

@hostel_bp.route("/", methods=["POST"])
@hostel_owner_required()
def create_hostel():

    data = request.get_json()

    required_fields = [
        "hostel_name",
        "address",
        "location",
        "description",
        "gender_type",
        "contact_no"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "message": f"{field} is required"
            }), 400

    owner_id = get_jwt_identity()

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO hostel
        (
            hostel_owner_id,
            hostel_name,
            address,
            location,
            description,
            gender_type,
            contact_no,
            status
        )
        VALUES
        (%s, %s, %s, %s, %s, %s, %s, 'Pending')
    """

    values = (
        owner_id,
        data["hostel_name"],
        data["address"],
        data["location"],
        data["description"],
        data["gender_type"],
        data["contact_no"]
    )

    cursor.execute(query, values)
    connection.commit()

    hostel_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Hostel created successfully and sent for admin approval",
        "hostel_id": hostel_id,
        "status": "Pending"
    }), 201

@hostel_bp.route("/<int:hostel_id>", methods=["PUT"])
@hostel_owner_required()
def update_hostel(hostel_id):

    data = request.get_json()

    required_fields = [
        "hostel_name",
        "address",
        "location",
        "description",
        "gender_type",
        "contact_no"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "message": f"{field} is required"
            }), 400

    owner_id = get_jwt_identity()

    connection = get_db_connection()
    cursor = connection.cursor()

    # Check whether this hostel belongs to the logged-in owner
    cursor.execute("""
        SELECT hostel_id
        FROM hostel
        WHERE hostel_id = %s
        AND hostel_owner_id = %s
    """, (hostel_id, owner_id))

    hostel = cursor.fetchone()

    if hostel is None:
        cursor.close()
        connection.close()

        return jsonify({
            "message": "You can update only your own hostel"
        }), 403

    # Update hostel
    cursor.execute("""
        UPDATE hostel
        SET hostel_name = %s,
            address = %s,
            location = %s,
            description = %s,
            gender_type = %s,
            contact_no = %s,
            status = 'Pending'
        WHERE hostel_id = %s
        AND hostel_owner_id = %s
    """, (
        data["hostel_name"],
        data["address"],
        data["location"],
        data["description"],
        data["gender_type"],
        data["contact_no"],
        hostel_id,
        owner_id
    ))

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Hostel updated successfully",
        "hostel_id": hostel_id,
        "status": "Pending"
    }), 200

@hostel_bp.route("/<int:hostel_id>", methods=["DELETE"])
@hostel_owner_required()
def delete_hostel(hostel_id):

    owner_id = get_jwt_identity()

    connection = get_db_connection()
    cursor = connection.cursor()

    # Check whether this hostel belongs to the logged-in owner
    cursor.execute("""
        SELECT hostel_id
        FROM hostel
        WHERE hostel_id = %s
        AND hostel_owner_id = %s
    """, (hostel_id, owner_id))

    hostel = cursor.fetchone()

    if hostel is None:
        cursor.close()
        connection.close()

        return jsonify({
            "message": "You can delete only your own hostel"
        }), 403

    # Delete hostel
    cursor.execute("""
        DELETE FROM hostel
        WHERE hostel_id = %s
        AND hostel_owner_id = %s
    """, (hostel_id, owner_id))

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Hostel deleted successfully",
        "hostel_id": hostel_id
    }), 200