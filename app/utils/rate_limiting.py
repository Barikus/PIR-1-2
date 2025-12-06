from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import jsonify

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",
    strategy="fixed-window",
    default_limits=["200 per day", "50 per hour"]
)

def add_rate_limit_headers(response, remaining: int = None):
    """Добавляет заголовки rate limiting в ответ"""
    if remaining is not None:
        response.headers["X-RateLimit-Remaining"] = str(remaining)
    return response
