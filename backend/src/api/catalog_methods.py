from flask import Blueprint, request, jsonify
import psycopg2

# Создаем Blueprint
catalog_bp = Blueprint('catalog', __name__)

# Переменная для хранения параметров подключения
db_config = {}

def set_db_config(config):
    """Устанавливаем параметры подключения к базе данных."""
    global db_config
    db_config = config

def get_db_connection():
    """Создаем подключение к базе данных."""
    return psycopg2.connect(**db_config)

# Эндпоинт для получения каталога с фильтрацией и сортировкой
@catalog_bp.route('/catalog', methods=['GET'])
def get_catalog():
    try:
        # Получение фильтров из запроса
        filters = request.args
        price_min = filters.get('price_min', type=float)
        price_max = filters.get('price_max', type=float)
        year_min = filters.get('year_min', type=int)
        year_max = filters.get('year_max', type=int)
        search = filters.get('search', type=str)
        sort_by = filters.get('sort_by', type=str)

        # Условия для SQL-запроса
        conditions = []
        params = []

        # Добавление фильтров
        if price_min is not None:
            conditions.append("price >= %s")
            params.append(price_min)
        if price_max is not None:
            conditions.append("price <= %s")
            params.append(price_max)
        if year_min is not None:
            conditions.append("year >= %s")
            params.append(year_min)
        if year_max is not None:
            conditions.append("year <= %s")
            params.append(year_max)
        if search:
            conditions.append("title ILIKE %s")
            params.append(f"%{search}%")

        # Базовый запрос
        query = "SELECT id, title, price, year FROM items"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # Добавление сортировки
        if sort_by == "price_asc":
            query += " ORDER BY price ASC"
        elif sort_by == "price_desc":
            query += " ORDER BY price DESC"
        elif sort_by == "year_asc":
            query += " ORDER BY year ASC"
        elif sort_by == "year_desc":
            query += " ORDER BY year DESC"

        # Подключение к базе и выполнение запроса
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query, tuple(params))
        results = cur.fetchall()
        cur.close()
        conn.close()

        # Формирование ответа
        catalog = [
            {"id": row[0], "title": row[1], "price": row[2], "year": row[3]}
            for row in results
        ]

        return jsonify(catalog), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Эндпоинт для получения подробной информации о товаре
@catalog_bp.route('/product/<int:product_id>', methods=['GET'])
def get_product_details(product_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Запрос на получение информации о товаре по ID
        cur.execute("""
            SELECT id, title, price, year, description, location 
            FROM items WHERE id = %s
        """, (product_id,))
        product = cur.fetchone()

        if product is None:
            return jsonify({"error": "Product not found"}), 404

        # Запрос на получение среднего рейтинга товара
        cur.execute("""
            SELECT AVG(stars) FROM ratings WHERE item_id = %s
        """, (product_id,))
        avg_rating = cur.fetchone()[0]
        avg_rating = round(avg_rating) if avg_rating is not None else None

        cur.close()
        conn.close()

        # Формирование ответа
        product_details = {
            "id": product[0],
            "title": product[1],
            "price": product[2],
            "year": product[3],
            "description": product[4],
            "location": product[5],
            "average_rating": avg_rating
        }

        return jsonify(product_details), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Эндпоинт для добавления рейтинга товару
@catalog_bp.route('/product/<int:product_id>/rating', methods=['POST'])
def add_product_rating(product_id):
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        stars = data.get('stars')

        if not user_id or stars is None:
            return jsonify({"error": "User ID and stars are required"}), 400

        if not (1 <= stars <= 5):
            return jsonify({"error": "Stars must be between 1 and 5"}), 400

        conn = get_db_connection()
        cur = conn.cursor()

        # Проверяем, поставил ли уже пользователь рейтинг для этого товара
        cur.execute("""
            SELECT id FROM ratings WHERE item_id = %s AND user_id = %s
        """, (product_id, user_id))
        if cur.fetchone():
            return jsonify({"error": "User has already rated this product"}), 400

        # Добавление рейтинга в базу данных
        cur.execute("""
            INSERT INTO ratings (item_id, user_id, stars) 
            VALUES (%s, %s, %s)
        """, (product_id, user_id, stars))
        conn.commit()

        cur.close()
        conn.close()

        return jsonify({"message": "Rating added successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

