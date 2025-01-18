from flask import Flask
from api.users import users_bp, set_db_config  # Импортируем Blueprint из обновленного файла users.py

app = Flask(__name__)

# Конфигурация базы данных
DB_CONFIG = {
    "dbname": "app_db",
    "user": "app_user",
    "password": "app_password",
    "host": "localhost",
    "port": "5432"
}

# Передаём конфигурацию базы данных в файл users.py
set_db_config(DB_CONFIG)

# Регистрируем Blueprint для работы с пользователями
app.register_blueprint(users_bp, url_prefix='/api/users')

# Главная страница (для проверки)
@app.route('/')
def home():
    return {"message": "API is working!"}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
