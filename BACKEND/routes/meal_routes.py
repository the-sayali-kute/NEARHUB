from flask import Blueprint, jsonify, request
from db import get_db_connection
from flask_jwt_extended import get_jwt_identity, get_jwt, verify_jwt_in_request

meal_bp = Blueprint(
    "meal",
    __name__,
    url_prefix="/api"
)


@meal_bp.route("/menus/", methods=["GET"])
def get_menus():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            menu.menu_id,
            menu.mess_id,
            mess.mess_name,
            menu.day,
            menu.meal_type,
            menu.food_items,
            menu.description
        FROM menu
        JOIN mess
            ON menu.mess_id = mess.mess_id
        ORDER BY menu.mess_id, menu.menu_id
    """)

    menus = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(menus)


@meal_bp.route("/menus/mess/<int:mess_id>", methods=["GET"])
def get_mess_menu(mess_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            menu_id,
            mess_id,
            day,
            meal_type,
            food_items,
            description
        FROM menu
        WHERE mess_id = %s
AND mess_id IN (
    SELECT mess_id
    FROM mess
    WHERE status = 'Approved'
)
        ORDER BY menu_id
    """, (mess_id,))

    menus = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(menus)


@meal_bp.route("/meal-plans/", methods=["GET"])
def get_meal_plans():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
    SELECT
        mp.plan_id,
        mp.mess_id,
        m.mess_name,
        mp.plan_name,
        mp.meals_per_day,
        mp.price,
        mp.duration,
        mp.description
    FROM meal_plan mp
    JOIN mess m
        ON mp.mess_id = m.mess_id
    WHERE m.status = 'Approved'
    ORDER BY mp.plan_id
""")

    plans = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(plans)


@meal_bp.route("/meal-plans/<int:plan_id>", methods=["GET"])
def get_meal_plan(plan_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
    SELECT
        mp.plan_id,
        mp.mess_id,
        m.mess_name,
        mp.plan_name,
        mp.meals_per_day,
        mp.price,
        mp.duration,
        mp.description
    FROM meal_plan mp
    JOIN mess m
        ON mp.mess_id = m.mess_id
    WHERE m.status = 'Approved'
    ORDER BY mp.plan_id
""")

    plan = cursor.fetchone()

    cursor.close()
    connection.close()

    if plan is None:
        return jsonify({
            "message": "Meal plan not found"
        }), 404

    return jsonify(plan)



# ADD MEAL PLAN
@meal_bp.route("/meal-plans/", methods=["POST"])
def add_meal_plan():

    # Check JWT
    verify_jwt_in_request()

    claims = get_jwt()
    owner_id = get_jwt_identity()
    role = claims.get("role")

    data = request.get_json()

    required_fields = [
        "mess_id",
        "plan_name",
        "meals_per_day",
        "price",
        "duration"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "message": f"{field} is required"
            }), 400

    # Basic validation
    if data["meals_per_day"] <= 0:
        return jsonify({
            "message": "Meals per day must be greater than 0"
        }), 400

    if data["price"] <= 0:
        return jsonify({
            "message": "Price must be greater than 0"
        }), 400

    if data["duration"] <= 0:
        return jsonify({
            "message": "Duration must be greater than 0"
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    # Check ownership of mess
    if role == "hostel_owner":

        cursor.execute("""
            SELECT mess_id
            FROM mess
            WHERE mess_id = %s
            AND hostel_owner_id = %s
        """, (data["mess_id"], owner_id))

    elif role == "mess_owner":

        cursor.execute("""
            SELECT mess_id
            FROM mess
            WHERE mess_id = %s
            AND mess_owner_id = %s
        """, (data["mess_id"], owner_id))

    else:
        cursor.close()
        connection.close()

        return jsonify({
            "message": "Only hostel owners and mess owners can add meal plans"
        }), 403

    mess = cursor.fetchone()

    if mess is None:
        cursor.close()
        connection.close()

        return jsonify({
            "message": "You can add meal plans only to your own mess"
        }), 403

    # Insert meal plan
    cursor.execute("""
        INSERT INTO meal_plan
        (
            mess_id,
            plan_name,
            meals_per_day,
            price,
            duration,
            description
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        data["mess_id"],
        data["plan_name"],
        data["meals_per_day"],
        data["price"],
        data["duration"],
        data.get("description")
    ))

    connection.commit()

    new_plan_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Meal plan added successfully",
        "plan_id": new_plan_id
    }), 201



# UPDATE MEAL PLAN
@meal_bp.route("/meal-plans/<int:plan_id>", methods=["PUT"])
def update_meal_plan(plan_id):

    # Check JWT
    verify_jwt_in_request()

    claims = get_jwt()
    owner_id = get_jwt_identity()
    role = claims.get("role")

    data = request.get_json()

    required_fields = [
        "plan_name",
        "meals_per_day",
        "price",
        "duration"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "message": f"{field} is required"
            }), 400

    # Basic validation
    if data["meals_per_day"] <= 0:
        return jsonify({
            "message": "Meals per day must be greater than 0"
        }), 400

    if data["price"] <= 0:
        return jsonify({
            "message": "Price must be greater than 0"
        }), 400

    if data["duration"] <= 0:
        return jsonify({
            "message": "Duration must be greater than 0"
        }), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    # Check ownership of the meal plan
    if role == "hostel_owner":

        cursor.execute("""
            SELECT mp.plan_id
            FROM meal_plan mp
            JOIN mess m
                ON mp.mess_id = m.mess_id
            WHERE mp.plan_id = %s
            AND m.hostel_owner_id = %s
        """, (plan_id, owner_id))

    elif role == "mess_owner":

        cursor.execute("""
            SELECT mp.plan_id
            FROM meal_plan mp
            JOIN mess m
                ON mp.mess_id = m.mess_id
            WHERE mp.plan_id = %s
            AND m.mess_owner_id = %s
        """, (plan_id, owner_id))

    else:
        cursor.close()
        connection.close()

        return jsonify({
            "message": "Only hostel owners and mess owners can update meal plans"
        }), 403

    plan = cursor.fetchone()

    if plan is None:
        cursor.close()
        connection.close()

        return jsonify({
            "message": "You can update only meal plans of your own mess"
        }), 403

    # Update meal plan
    cursor.execute("""
        UPDATE meal_plan
        SET plan_name = %s,
            meals_per_day = %s,
            price = %s,
            duration = %s,
            description = %s
        WHERE plan_id = %s
    """, (
        data["plan_name"],
        data["meals_per_day"],
        data["price"],
        data["duration"],
        data.get("description"),
        plan_id
    ))

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Meal plan updated successfully",
        "plan_id": plan_id
    }), 200

# DELETE MEAL PLAN
@meal_bp.route("/meal-plans/<int:plan_id>", methods=["DELETE"])
def delete_meal_plan(plan_id):

    # Check JWT
    verify_jwt_in_request()

    claims = get_jwt()
    owner_id = get_jwt_identity()
    role = claims.get("role")

    connection = get_db_connection()
    cursor = connection.cursor()

    # Check ownership of the meal plan
    if role == "hostel_owner":

        cursor.execute("""
            SELECT mp.plan_id
            FROM meal_plan mp
            JOIN mess m
                ON mp.mess_id = m.mess_id
            WHERE mp.plan_id = %s
            AND m.hostel_owner_id = %s
        """, (plan_id, owner_id))

    elif role == "mess_owner":

        cursor.execute("""
            SELECT mp.plan_id
            FROM meal_plan mp
            JOIN mess m
                ON mp.mess_id = m.mess_id
            WHERE mp.plan_id = %s
            AND m.mess_owner_id = %s
        """, (plan_id, owner_id))

    else:
        cursor.close()
        connection.close()

        return jsonify({
            "message": "Only hostel owners and mess owners can delete meal plans"
        }), 403

    plan = cursor.fetchone()

    if plan is None:
        cursor.close()
        connection.close()

        return jsonify({
            "message": "You can delete only meal plans of your own mess"
        }), 403

    # Delete meal plan
    cursor.execute("""
        DELETE FROM meal_plan
        WHERE plan_id = %s
    """, (plan_id,))

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Meal plan deleted successfully",
        "plan_id": plan_id
    }), 200





# ADD MENU
@meal_bp.route("/menus/", methods=["POST"])
def add_menu():

    # Check JWT
    verify_jwt_in_request()

    claims = get_jwt()
    owner_id = get_jwt_identity()
    role = claims.get("role")

    data = request.get_json()

    required_fields = [
        "mess_id",
        "day",
        "meal_type",
        "food_items"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "message": f"{field} is required"
            }), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    # Check whether the mess belongs to the logged-in owner
    if role == "hostel_owner":

        cursor.execute("""
            SELECT mess_id
            FROM mess
            WHERE mess_id = %s
            AND hostel_owner_id = %s
        """, (data["mess_id"], owner_id))

    elif role == "mess_owner":

        cursor.execute("""
            SELECT mess_id
            FROM mess
            WHERE mess_id = %s
            AND mess_owner_id = %s
        """, (data["mess_id"], owner_id))

    else:
        cursor.close()
        connection.close()

        return jsonify({
            "message": "Only hostel owners and mess owners can add menus"
        }), 403

    mess = cursor.fetchone()

    if mess is None:
        cursor.close()
        connection.close()

        return jsonify({
            "message": "You can add menu only to your own mess"
        }), 403

    # Insert menu
    cursor.execute("""
        INSERT INTO menu
        (
            mess_id,
            day,
            meal_type,
            food_items,
            description
        )
        VALUES (%s, %s, %s, %s, %s)
    """, (
        data["mess_id"],
        data["day"],
        data["meal_type"],
        data["food_items"],
        data.get("description")
    ))

    connection.commit()

    new_menu_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Menu added successfully",
        "menu_id": new_menu_id
    }), 201

# UPDATE MENU
@meal_bp.route("/menus/<int:menu_id>", methods=["PUT"])
def update_menu(menu_id):

    # Check JWT
    verify_jwt_in_request()

    claims = get_jwt()
    owner_id = get_jwt_identity()
    role = claims.get("role")

    data = request.get_json()

    required_fields = [
        "day",
        "meal_type",
        "food_items"
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({
                "message": f"{field} is required"
            }), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    # Check whether menu belongs to the logged-in owner's mess
    if role == "hostel_owner":

        cursor.execute("""
            SELECT menu.menu_id
            FROM menu
            JOIN mess
                ON menu.mess_id = mess.mess_id
            WHERE menu.menu_id = %s
            AND mess.hostel_owner_id = %s
        """, (menu_id, owner_id))

    elif role == "mess_owner":

        cursor.execute("""
            SELECT menu.menu_id
            FROM menu
            JOIN mess
                ON menu.mess_id = mess.mess_id
            WHERE menu.menu_id = %s
            AND mess.mess_owner_id = %s
        """, (menu_id, owner_id))

    else:
        cursor.close()
        connection.close()

        return jsonify({
            "message": "Only hostel owners and mess owners can update menus"
        }), 403

    menu = cursor.fetchone()

    if menu is None:
        cursor.close()
        connection.close()

        return jsonify({
            "message": "You can update only menus of your own mess"
        }), 403

    # Update menu
    cursor.execute("""
        UPDATE menu
        SET day = %s,
            meal_type = %s,
            food_items = %s,
            description = %s
        WHERE menu_id = %s
    """, (
        data["day"],
        data["meal_type"],
        data["food_items"],
        data.get("description"),
        menu_id
    ))

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Menu updated successfully",
        "menu_id": menu_id
    }), 200

# DELETE MENU
@meal_bp.route("/menus/<int:menu_id>", methods=["DELETE"])
def delete_menu(menu_id):

    # Check JWT
    verify_jwt_in_request()

    claims = get_jwt()
    owner_id = get_jwt_identity()
    role = claims.get("role")

    connection = get_db_connection()
    cursor = connection.cursor()

    # Check whether menu belongs to logged-in owner's mess
    if role == "hostel_owner":

        cursor.execute("""
            SELECT menu.menu_id
            FROM menu
            JOIN mess
                ON menu.mess_id = mess.mess_id
            WHERE menu.menu_id = %s
            AND mess.hostel_owner_id = %s
        """, (menu_id, owner_id))

    elif role == "mess_owner":

        cursor.execute("""
            SELECT menu.menu_id
            FROM menu
            JOIN mess
                ON menu.mess_id = mess.mess_id
            WHERE menu.menu_id = %s
            AND mess.mess_owner_id = %s
        """, (menu_id, owner_id))

    else:
        cursor.close()
        connection.close()

        return jsonify({
            "message": "Only hostel owners and mess owners can delete menus"
        }), 403

    menu = cursor.fetchone()

    if menu is None:
        cursor.close()
        connection.close()

        return jsonify({
            "message": "You can delete only menus of your own mess"
        }), 403

    # Delete menu
    cursor.execute("""
        DELETE FROM menu
        WHERE menu_id = %s
    """, (menu_id,))

    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({
        "message": "Menu deleted successfully",
        "menu_id": menu_id
    }), 200