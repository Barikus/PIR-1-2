import os
from flask import Flask
from flask_restful import Api
from flasgger import Swagger
from app.utils.rate_limiting import limiter
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Инициализация расширений
    api = Api(app, prefix="/api")
    
    swagger_config_path = os.path.join(app.root_path, 'docs', 'swagger.yaml')

    app.config["SWAGGER"] = {
        "title": "Book Reviews API",
        "uiversion": 3,
        "specs_route": "/apidocs/",
    }
    
    swagger = Swagger(app, template_file=swagger_config_path)
    
    limiter.init_app(app)
    
    # Регистрация маршрутов
    from app.routes.books import register_book_routes
    from app.routes.auth import register_auth_routes
    from app.routes.reviews import register_review_routes
    from app.routes.internal import register_internal_routes
    
    register_auth_routes(api)
    register_book_routes(api)
    register_review_routes(api)
    register_internal_routes(api)
    
    return app
