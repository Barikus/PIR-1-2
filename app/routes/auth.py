from flask_restful import Resource, reqparse
from app.models import users_db
from app.auth.jwt_auth import generate_token
from app.utils.rate_limiting import limiter

class AuthLogin(Resource):
    @limiter.limit("10 per minute")
    def post(self):
        """Вход пользователя"""
        parser = reqparse.RequestParser()
        parser.add_argument("username", type=str, required=True, help="Username required")
        parser.add_argument("email", type=str, required=True, help="Email required")
        args = parser.parse_args()
        
        # Поиск пользователя
        user = next(
            (u for u in users_db.values() 
             if u.username == args["username"] and u.email == args["email"]),
            None
        )
        
        if not user:
            return {"error": "Invalid credentials"}, 401
        
        token = generate_token(user.id, user.username)
        return {"token": token, "user_id": user.id, "username": user.username}, 200

def register_auth_routes(api):
    api.add_resource(AuthLogin, "/v1/auth/login", "/v2/auth/login")
