import jwt
import datetime
from functools import wraps
from flask import request, jsonify
from app.config import Config

def generate_token(user_id: int, username: str) -> str:
    """Генерирует JWT токен"""
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.datetime.utcnow() + Config.JWT_ACCESS_TOKEN_EXPIRES,
        "iat": datetime.datetime.utcnow(),
    }
    token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")
    return token

def verify_token(token: str) -> dict:
    """Проверяет JWT токен"""
    try:
        payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return {"error": "Токен истек"}
    except jwt.InvalidTokenError as e:
        return {"error": f"Неверный токен: {str(e)}"}
    except Exception as e:
        return {"error": "Ошибка сервера при проверке токена"}

def token_required(f):
    """Декоратор для защиты маршрутов с помощью JWT"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        auth_header = request.headers.get("Authorization")

        if auth_header:
            parts = auth_header.split()
            token = parts[1]
            
            # Очистка от случайных кавычек
            token = token.strip().strip('"').strip("'")

        
        if not token:
            return {"error": "Токен отсутствует или неверный формат заголовка"}, 401
        
        # Проверяем токен
        payload = verify_token(token)
        
        if "error" in payload:
            return {"error": payload["error"]}, 401
        
        # Добавляем информацию о пользователе в контекст запроса
        request.current_user = payload
        
        return f(*args, **kwargs)
    
    return decorated
