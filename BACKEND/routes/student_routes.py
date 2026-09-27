from flask import Blueprint, jsonify, request
from db import get_db_connection
from routes.auth_utils import student_required
from flask_jwt_extended import get_jwt_identity

student_bp = Blueprint(
    "student",
    __name__,
    url_prefix="/api/students"
)


@student_bp.route("/", methods=["GET"])
def get_students():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            student_id,
            name,
            email,
            phone,
            gender,
            college,
            course,
            year,
            budget,
            preferred_location,
            created_at
        FROM student
    """)

    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(students)


@student_bp.route("/<int:student_id>", methods=["GET"])
@student_required()
def get_student(student_id):

    logged_in_student_id = int(get_jwt_identity())

    # Student can access only their own profile
    if student_id != logged_in_student_id:
        return jsonify({
            "message": "You can access only your own profile"
        }), 403

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            student_id,
            name,
            email,
            phone,
            gender,
            college,
            course,
            year,
            budget,
            preferred_location,
            created_at
        FROM student
        WHERE student_id = %s
    """, (student_id,))

    student = cursor.fetchone()

    cursor.close()
    connection.close()

    if student is None:
        return jsonify({
            "message": "Student not found"
        }), 404

    return jsonify(student)


@student_bp.route("/", methods=["POST"])
def add_student():
    data = request.get_json()

    required_fields = [
        "name",
        "email",
        "phone",
        "password_hash",
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

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO student
        (name, email, phone, password_hash, gender, college,
         course, year, budget, preferred_location)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        data["name"],
        data["email"],
        data["phone"],
        data["password_hash"],
        data["gender"],
        data["college"],
        data["course"],
        data["year"],
        data["budget"],
        data["preferred_location"]
    )

    cursor.execute(query, values)
    connection.commit()

    new_student_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Student added successfully",
        "student_id": new_student_id
    }), 201