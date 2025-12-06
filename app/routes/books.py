from flask_restful import Resource, reqparse
from flask import jsonify, request
from app.models import books_db, reviews_db, Book, BookV2
from app.auth.jwt_auth import token_required
from app.utils.pagination import Paginator
from app.utils.rate_limiting import limiter, add_rate_limit_headers
from app.utils.idempotency import idempotent_request

book_parser_v1 = reqparse.RequestParser()
book_parser_v1.add_argument("title", type=str, required=True, help="Title required")
book_parser_v1.add_argument("author", type=str, required=True, help="Author required")
book_parser_v1.add_argument("published_year", type=int, required=True, help="Year required")
book_parser_v1.add_argument("isbn", type=str)

book_parser_v2 = reqparse.RequestParser()
book_parser_v2.add_argument("title", type=str, required=True)
book_parser_v2.add_argument("author", type=str, required=True)
book_parser_v2.add_argument("published_year", type=int, required=True)
book_parser_v2.add_argument("isbn", type=str)
book_parser_v2.add_argument("publisher", type=str)
book_parser_v2.add_argument("genre", type=str)

class BookListV1(Resource):
    @limiter.limit("100 per hour")
    def get(self):
        """Получить список книг (v1)"""
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        
        books_list = list(books_db.values())
        paginator = Paginator(books_list, page, per_page)
        paginated = paginator.paginate()
        
        response = jsonify({
            "books": [book.to_dict() for book in paginated],
            "pagination": paginator.get_pagination_metadata()
        })
        
        return add_rate_limit_headers(response, 95)
    
    @token_required
    @idempotent_request
    @limiter.limit("50 per hour")
    def post(self):
        """Создать новую книгу (v1)"""
        args = book_parser_v1.parse_args()
        book_id = max(books_db.keys()) + 1 if books_db else 1
        
        book = Book(
            id=book_id,
            title=args["title"],
            author=args["author"],
            published_year=args["published_year"],
            isbn=args.get("isbn")
        )
        
        books_db[book_id] = book
        return book.to_dict(), 201

class BookDetailV1(Resource):
    def get(self, book_id):
        """Получить книгу по ID (v1)"""
        if book_id not in books_db:
            return {"error": "Book not found"}, 404
        return books_db[book_id].to_dict(), 200
    
    @token_required
    def put(self, book_id):
        """Обновить книгу (v1)"""
        if book_id not in books_db:
            return {"error": "Book not found"}, 404
        
        args = book_parser_v1.parse_args()
        book = books_db[book_id]
        
        book.title = args["title"]
        book.author = args["author"]
        book.published_year = args["published_year"]
        if args.get("isbn"):
            book.isbn = args["isbn"]
        
        return book.to_dict(), 200
    
    @token_required
    def delete(self, book_id):
        """Удалить книгу (v1)"""
        if book_id not in books_db:
            return {"error": "Book not found"}, 404
        
        del books_db[book_id]
        return "", 204

class BookListV2(Resource):
    @limiter.limit("150 per hour")
    def get(self):
        """Получить список книг (v2) с опциональными полями"""
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        include = request.args.get("include", "")
        
        include_fields = [f.strip().lower() for f in include.split(",") if f.strip()]
        
        books_list = list(books_db.values())
        paginator = Paginator(books_list, page, per_page)
        paginated = paginator.paginate()
        
        response_books = []
        for book in paginated:
            book_dict = book.to_dict()
            
            if "reviews" in include_fields:
                book_dict["reviews"] = [
                    r.to_dict() for r in reviews_db.values() 
                    if r.book_id == book.id
                ]
            
            if "stats" in include_fields:
                book_reviews = [r for r in reviews_db.values() if r.book_id == book.id]
                if book_reviews:
                    avg_rating = sum(r.rating for r in book_reviews) / len(book_reviews)
                else:
                    avg_rating = 0
                
                book_dict["stats"] = {
                    "review_count": len(book_reviews),
                    "average_rating": round(avg_rating, 2)
                }
            
            response_books.append(book_dict)
        
        response = jsonify({
            "books": response_books,
            "pagination": paginator.get_pagination_metadata()
        })
        
        return add_rate_limit_headers(response, 145)
    
    @token_required
    @idempotent_request
    @limiter.limit("60 per hour")
    def post(self):
        """Создать новую книгу (v2)"""
        args = book_parser_v2.parse_args()
        book_id = max(books_db.keys()) + 1 if books_db else 1
        
        book = BookV2(
            id=book_id,
            title=args["title"],
            author=args["author"],
            published_year=args["published_year"],
            isbn=args.get("isbn"),
            publisher=args.get("publisher"),
            genre=args.get("genre")
        )
        
        books_db[book_id] = book
        return book.to_dict(), 201

def register_book_routes(api):
    api.add_resource(BookListV1, "/v1/books")
    api.add_resource(BookDetailV1, 
                     "/v1/books/<int:book_id>", 
                     "/v2/books/<int:book_id>")
                     
    api.add_resource(BookListV2, "/v2/books")
