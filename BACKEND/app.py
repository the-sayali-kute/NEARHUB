from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from routes.student_routes import student_bp
from routes.hostel_routes import hostel_bp
from routes.room_routes import room_bp
from routes.mess_routes import mess_bp
from routes.meal_routes import meal_bp
from routes.booking_routes import booking_bp
from routes.subscription_routes import subscription_bp
from routes.feedback_routes import feedback_bp
from routes.preference_routes import preference_bp
from routes.admin_routes import admin_bp
from routes.auth_routes import auth_bp


app = Flask(__name__)
CORS(app)

import os
from dotenv import load_dotenv

load_dotenv()

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)

app.register_blueprint(student_bp)
app.register_blueprint(hostel_bp)
app.register_blueprint(room_bp)
app.register_blueprint(mess_bp)
app.register_blueprint(meal_bp)
app.register_blueprint(booking_bp)
app.register_blueprint(subscription_bp)
app.register_blueprint(feedback_bp)
app.register_blueprint(preference_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)

@app.route("/")
def home():
    return "NearHub Backend is Running!"


@app.route("/api/test-db")
def test_db():
    from db import get_db_connection

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT DATABASE()")
    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return {
        "message": "Database connected successfully",
        "database": result[0]
    }


if __name__ == "__main__":
    app.run(debug=True)