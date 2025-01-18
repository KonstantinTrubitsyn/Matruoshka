from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2

# Создаем Blueprint
users_bp = Blueprint('users', __name__)

# Переменная для хранения параметров подключения
db_config = {}

def set_db_config(config):
    """Устанавливаем параметры подключения к базе данных."""
    global db_config
    db_config = config

def get_db_connection():
    """Создаем подключение к базе данных."""
    return psycopg2.connect(**db_config)

# Маршрут для регистрации пользователя
@users_bp.route('/register', methods=['POST'])
def register_user():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            return jsonify({"error": "Email is already in use"}), 400

        cur.execute(
            "INSERT INTO users (email, password) VALUES (%s, %s)",
            (email, hashed_password)
        )
        conn.commit()

        cur.close()
        conn.close()

        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Маршрут для авторизации пользователя
@users_bp.route('/login', methods=['POST'])
def login_user():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Проверяем, существует ли пользователь с таким email
        cur.execute("SELECT id, password FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if not user:
            return jsonify({"error": "Invalid email or password"}), 401

        # Проверяем пароль
        user_id, hashed_password = user
        if not check_password_hash(hashed_password, password):
            return jsonify({"error": "Invalid email or password"}), 401

        # Успешный ответ
        return jsonify({
            "message": "Login successful",
            "user_id": user_id,
            "email": email
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
