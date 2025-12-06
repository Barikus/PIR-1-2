import os
from datetime import timedelta

class Config:
    # Основная конфигурация
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key"
    
    # JWT конфигурация
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "jwt-secret-key"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Ограничение частоты запросов
    RATELIMIT_STORAGE_URL = "memory://"
    RATELIMIT_STRATEGY = "fixed-window"
    RATELIMIT_DEFAULT = "200 per day, 50 per hour"
    
    # Ключ внутреннего API
    INTERNAL_API_KEY = os.environ.get("INTERNAL_API_KEY") or "internal-secret-key"
