from flask_restful import Resource
from flask import request
from datetime import datetime
from app.models import books_db, users_db, reviews_db
from app.config import Config

class InternalStats(Resource):
    def get(self):
        """Получить статистику системы (только внутреннее API)"""
        
        # Проверка X-API-Key
        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key != Config.INTERNAL_API_KEY:
            return {"error": "Unauthorized"}, 401
        
        # Вычисление статистики
        total_books = len(books_db)
        total_users = len(users_db)
        total_reviews = len(reviews_db)
        
        # Средняя оценка
        if total_reviews > 0:
            avg_rating = sum(r.rating for r in reviews_db.values()) / total_reviews
        else:
            avg_rating = 0
        
        # Самые рецензируемые книги
        book_review_counts = {}
        for review in reviews_db.values():
            book_review_counts[review.book_id] = book_review_counts.get(review.book_id, 0) + 1
        
        most_reviewed = sorted(
            book_review_counts.items(),
            key=lambda x: x,
            reverse=True
        )[:5]
        
        most_reviewed_books = [
            {
                "book_id": book_id,
                "book_title": books_db[book_id].title if book_id in books_db else "Unknown",
                "review_count": count
            }
            for book_id, count in most_reviewed
        ]
        
        return {
            "total_books": total_books,
            "total_users": total_users,
            "total_reviews": total_reviews,
            "average_rating": round(avg_rating, 2),
            "most_reviewed_books": most_reviewed_books,
            "system_health": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        }, 200

def register_internal_routes(api):
    api.add_resource(InternalStats, "/internal/stats")
