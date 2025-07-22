from sanic import Blueprint

from app.apis.books_blueprint import books_bp
from app.apis.example_blueprint import example
from app.apis.users_blueprint import users_bp

api = Blueprint.group(example, books_bp, users_bp)
