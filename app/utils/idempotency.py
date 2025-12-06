from functools import wraps
from flask import request
from app.models import idempotency_store

def idempotent_request(f):
    """Декоратор для обеспечения идемпотентности"""
    @wraps(f)
    def decorated(*args, **kwargs):
        idempotency_key = request.headers.get("Idempotency-Key")
        
        if idempotency_key:
            if idempotency_key in idempotency_store:
                # Повторный запрос - вернуть сохранённый результат
                stored = idempotency_store[idempotency_key]
                return stored["data"], stored["status"]
        
        # Выполнить операцию
        result = f(*args, **kwargs)
        
        # Сохранить результат для будущих повторов
        if idempotency_key:
            if isinstance(result, tuple):
                data, status = result, result if len(result) > 1 else 200
            else:
                data, status = result, 200
            
            idempotency_store[idempotency_key] = {"data": data, "status": status}
        
        return result
    
    return decorated
