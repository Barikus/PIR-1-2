from flask_restful import Resource, reqparse
from flask import jsonify, request
from app.models import reviews_db, books_db, Review
from app.auth.jwt_auth import token_required
from app.utils.pagination import Paginator
from app.utils.rate_limiting import limiter, add_rate_limit_headers
from app.utils.idempotency import idempotent_request

# --- ПАРСЕР ДЛЯ СОЗДАНИЯ (POST) ---
create_review_parser = reqparse.RequestParser()
create_review_parser.add_argument("book_id", type=int, required=True, help="Book ID is required")
create_review_parser.add_argument("rating", type=int, required=True, help="Rating is required")
create_review_parser.add_argument("text", type=str, required=True, help="Text is required")

# --- ПАРСЕР ДЛЯ ОБНОВЛЕНИЯ (PUT) ---
update_review_parser = reqparse.RequestParser()
update_review_parser.add_argument("rating", type=int, required=True, help="Rating is required")
update_review_parser.add_argument("text", type=str, required=True, help="Text is required")

class ReviewList(Resource):
    @limiter.limit("100 per hour")
    def get(self):
        """Получить список рецензий"""
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        
        reviews_list = list(reviews_db.values())
        paginator = Paginator(reviews_list, page, per_page)
        paginated = paginator.paginate()
        
        reviews_with_details = []
        for review in paginated:
            review_dict = review.to_dict()
            book = books_db.get(review.book_id)
            if book:
                review_dict["book_title"] = book.title
                review_dict["book_author"] = book.author
            reviews_with_details.append(review_dict)
        
        response = jsonify({
            "reviews": reviews_with_details,
            "pagination": paginator.get_pagination_metadata()
        })
        
        return add_rate_limit_headers(response, 95)
    
    @token_required
    @idempotent_request
    @limiter.limit("50 per hour")
    def post(self):
        """Создать новую рецензию"""
        args = create_review_parser.parse_args()
        
        if args["book_id"] not in books_db:
            return {"error": "Book not found"}, 404
        
        review_id = max(reviews_db.keys()) + 1 if reviews_db else 1
        
        # Получаем user_id из токена (установлен декоратором @token_required)
        current_user_id = request.current_user["user_id"]
        current_username = request.current_user["username"]

        review = Review(
            id=review_id,
            book_id=args["book_id"],
            user_id=current_user_id,
            rating=args["rating"],
            text=args["text"]
        )
        
        reviews_db[review_id] = review
        
        # Формируем ответ с деталями
        review_dict = review.to_dict()
        book = books_db[args["book_id"]]
        review_dict["book_title"] = book.title
        review_dict["book_author"] = book.author
        review_dict["username"] = current_username
        
        return review_dict, 201

class ReviewDetail(Resource):
    def get(self, review_id):
        """Получить рецензию по ID"""
        if review_id not in reviews_db:
            return {"error": "Review not found"}, 404
        
        review = reviews_db[review_id]
        review_dict = review.to_dict()
        
        book = books_db.get(review.book_id)
        if book:
            review_dict["book_title"] = book.title
            review_dict["book_author"] = book.author
        
        return review_dict, 200
    
    @token_required
    def put(self, review_id):
        """Обновить рецензию"""
        if review_id not in reviews_db:
            return {"error": "Review not found"}, 404
        
        review = reviews_db[review_id]
        
        # Проверка прав: обновлять может только автор
        if review.user_id != request.current_user["user_id"]:
            return {"error": "Unauthorized: You can only edit your own reviews"}, 403
        
        args = update_review_parser.parse_args()
        
        review.rating = args["rating"]
        review.text = args["text"]
        
        review_dict = review.to_dict()
        book = books_db.get(review.book_id)
        if book:
            review_dict["book_title"] = book.title
            review_dict["book_author"] = book.author
        
        return review_dict, 200
    
    @token_required
    def delete(self, review_id):
        """Удалить рецензию"""
        if review_id not in reviews_db:
            return {"error": "Review not found"}, 404
        
        review = reviews_db[review_id]
        
        # Проверка прав: удалять может только автор
        if review.user_id != request.current_user["user_id"]:
            return {"error": "Unauthorized: You can only delete your own reviews"}, 403
        
        del reviews_db[review_id]
        return "", 204

def register_review_routes(api):
    # Регистрируем сразу для v1 и v2, так как логика одинаковая
    api.add_resource(ReviewList, "/v1/reviews", "/v2/reviews")
    api.add_resource(ReviewDetail, "/v1/reviews/<int:review_id>", "/v2/reviews/<int:review_id>")
