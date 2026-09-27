from flask import Blueprint, jsonify, request
from db import get_db_connection
from flask_jwt_extended import get_jwt_identity, get_jwt
from routes.auth_utils import role_required

mess_bp = Blueprint(
    "mess",
    __name__,
    url_prefix="/api/messes"
)


@mess_bp.route("/", methods=["GET"])
def get_messes():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
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
                WHEN m.hostel_owner_id IS NOT NULL THEN 'Hostel Owner'
                WHEN m.mess_owner_id IS NOT NULL THEN 'Mess Owner'
            END AS owner_type
        FROM mess m
WHERE m.status = 'Approved'
ORDER BY m.mess_id
    """)

    messes = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(messes)


@mess_bp.route("/<int:mess_id>", methods=["GET"])
def get_mess(mess_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
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
                WHEN m.hostel_owner_id IS NOT NULL THEN 'Hostel Owner'
                WHEN m.mess_owner_id IS NOT NULL THEN 'Mess Owner'
            END AS owner_type
        FROM mess m
        WHERE m.mess_id = %s
AND m.status = 'Approved'
    """, (mess_id,))

    mess = cursor.fetchone()

    cursor.close()
    connection.close()

    if mess is None:
        return jsonify({
            "message": "Mess not found"
        }), 404

    return jsonify(mess)

# GET MESSES OF A HOSTEL
@mess_bp.route("/hostel/<int:hostel_id>", methods=["GET"])
def get_hostel_messes(hostel_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
    SELECT
        mess_id,
        hostel_owner_id,
        mess_owner_id,
        mess_name,
        location,
        address,
        description,
        contact_no,
        food_type,
        status
    FROM mess
    WHERE hostel_owner_id = (
        SELECT hostel_owner_id
        FROM hostel
        WHERE hostel_id = %s
    )
    AND status = 'Approved'
""", (hostel_id,))

    messes = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(messes)

# ADD MESS
@mess_bp.route("/", methods=["POST"])
@role_required("hostel_owner")
def add_mess_as_hostel_owner():

    data = request.get_json()

    required_fields = [
        "mess_name",
        "location",
        "address",
        "description",
        "contact_no",
        "food_type"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "message": f"{field} is required"
            }), 400

    owner_id = get_jwt_identity()

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO mess
        (
            hostel_owner_id,
            mess_owner_id,
            mess_name,
            location,
            address,
            description,
            contact_no,
            food_type,
            status
        )
        VALUES (%s, NULL, %s, %s, %s, %s, %s, %s, 'Pending')
    """, (
        owner_id,
        data["mess_name"],
        data["location"],
        data["address"],
        data["description"],
        data["contact_no"],
        data["food_type"]
    ))

    connection.commit()

    new_mess_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Mess added successfully",
        "mess_id": new_mess_id,
        "status": "Pending"
    }), 201

# ADD MESS - MESS OWNER
@mess_bp.route("/mess-owner", methods=["POST"])
@role_required("mess_owner")
def add_mess_as_mess_owner():

    data = request.get_json()

    required_fields = [
        "mess_name",
        "location",
        "address",
        "description",
        "contact_no",
        "food_type"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "message": f"{field} is required"
            }), 400

    owner_id = get_jwt_identity()

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO mess
        (
            hostel_owner_id,
            mess_owner_id,
            mess_name,
            location,
            address,
            description,
            contact_no,
            food_type,
            status
        )
        VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, 'Pending')
    """, (
        owner_id,
        data["mess_name"],
        data["location"],
        data["address"],
        data["description"],
        data["contact_no"],
        data["food_type"]
    ))

    connection.commit()

    new_mess_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Mess added successfully",
        "mess_id": new_mess_id,
        "status": "Pending"
    }), 201

# UPDATE MESS
@mess_bp.route("/<int:mess_id>", methods=["PUT"])
@role_required("hostel_owner")
def update_mess_as_hostel_owner(mess_id):

    data = request.get_json()

    required_fields = [
        "mess_name",
        "location",
        "address",
        "description",
        "contact_no",
        "food_type"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "message": f"{field} is required"
            }), 400

    owner_id = get_jwt_identity()

    connection = get_db_connection()
    cursor = connection.cursor()

    # Check ownership
    cursor.execute("""
        SELECT mess_id
        FROM mess
        WHERE mess_id = %s
        AND hostel_owner_id = %s
    """, (mess_id, owner_id))

    mess = cursor.fetchone()

    if mess is None:
        cursor.close()
        connection.close()

        return jsonify({
            "message": "You can update only your own mess"
        }), 403

    # Update mess
    cursor.execute("""
        UPDATE mess
        SET mess_name = %s,
            location = %s,
            address = %s,
            description = %s,
            contact_no = %s,
            food_type = %s,
            status = 'Pending'
        WHERE mess_id = %s
        AND hostel_owner_id = %s
    """, (
        data["mess_name"],
        data["location"],
        data["address"],
        data["description"],
        data["contact_no"],
        data["food_type"],
        mess_id,
        owner_id
    ))

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Mess updated successfully",
        "mess_id": mess_id,
        "status": "Pending"
    }), 200

# UPDATE MESS - MESS OWNER
@mess_bp.route("/mess-owner/<int:mess_id>", methods=["PUT"])
@role_required("mess_owner")
def update_mess_as_mess_owner(mess_id):

    data = request.get_json()

    required_fields = [
        "mess_name",
        "location",
        "address",
        "description",
        "contact_no",
        "food_type"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "message": f"{field} is required"
            }), 400

    owner_id = get_jwt_identity()

    connection = get_db_connection()
    cursor = connection.cursor()

    # Check ownership
    cursor.execute("""
        SELECT mess_id
        FROM mess
        WHERE mess_id = %s
        AND mess_owner_id = %s
    """, (mess_id, owner_id))

    mess = cursor.fetchone()

    if mess is None:
        cursor.close()
        connection.close()

        return jsonify({
            "message": "You can update only your own mess"
        }), 403

    # Update mess
    cursor.execute("""
        UPDATE mess
        SET mess_name = %s,
            location = %s,
            address = %s,
            description = %s,
            contact_no = %s,
            food_type = %s,
            status = 'Pending'
        WHERE mess_id = %s
        AND mess_owner_id = %s
    """, (
        data["mess_name"],
        data["location"],
        data["address"],
        data["description"],
        data["contact_no"],
        data["food_type"],
        mess_id,
        owner_id
    ))

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Mess updated successfully",
        "mess_id": mess_id,
        "status": "Pending"
    }), 200

# DELETE MESS - HOSTEL OWNER
@mess_bp.route("/<int:mess_id>", methods=["DELETE"])
@role_required("hostel_owner")
def delete_mess_as_hostel_owner(mess_id):

    owner_id = get_jwt_identity()

    connection = get_db_connection()
    cursor = connection.cursor()

    # Check ownership
    cursor.execute("""
        SELECT mess_id
        FROM mess
        WHERE mess_id = %s
        AND hostel_owner_id = %s
    """, (mess_id, owner_id))

    mess = cursor.fetchone()

    if mess is None:
        cursor.close()
        connection.close()

        return jsonify({
            "message": "You can delete only your own mess"
        }), 403

    # Delete mess
    cursor.execute("""
        DELETE FROM mess
        WHERE mess_id = %s
        AND hostel_owner_id = %s
    """, (mess_id, owner_id))

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Mess deleted successfully",
        "mess_id": mess_id
    }), 200


# DELETE MESS - MESS OWNER
@mess_bp.route("/mess-owner/<int:mess_id>", methods=["DELETE"])
@role_required("mess_owner")
def delete_mess_as_mess_owner(mess_id):

    owner_id = get_jwt_identity()

    connection = get_db_connection()
    cursor = connection.cursor()

    # Check ownership
    cursor.execute("""
        SELECT mess_id
        FROM mess
        WHERE mess_id = %s
        AND mess_owner_id = %s
    """, (mess_id, owner_id))

    mess = cursor.fetchone()

    if mess is None:
        cursor.close()
        connection.close()

        return jsonify({
            "message": "You can delete only your own mess"
        }), 403

    # Delete mess
    cursor.execute("""
        DELETE FROM mess
        WHERE mess_id = %s
        AND mess_owner_id = %s
    """, (mess_id, owner_id))

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Mess deleted successfully",
        "mess_id": mess_id
    }), 200