from functools import wraps

from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt


def role_required(required_role):

    def decorator(function):

        @wraps(function)
        def wrapper(*args, **kwargs):

            verify_jwt_in_request()

            claims = get_jwt()

            if claims.get("role") != required_role:
                return jsonify({
                    "message": f"{required_role} access required"
                }), 403

            return function(*args, **kwargs)

        return wrapper

    return decorator


def student_required():
    return role_required("student")


def hostel_owner_required():
    return role_required("hostel_owner")


def mess_owner_required():
    return role_required("mess_owner")


def admin_required():
    return role_required("admin")