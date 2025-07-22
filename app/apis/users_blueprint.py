import uuid
from sanic import Blueprint
from sanic.response import json
from app.databases.mongodb import MongoDB
from app.decorators.json_validator import validate_with_jsonschema
from app.models.user import User, register_json_schema, login_json_schema
from app.hooks.error import ApiInternalError
from app.utils.jwt_utils import generate_jwt

users_bp = Blueprint('users_blueprint', url_prefix='/users')
_db = MongoDB()

@users_bp.route('/register', methods=['POST'])
@validate_with_jsonschema(register_json_schema)
async def register_user(request):
    body = request.json
    username = body['username']

    if _db.get_user_by_username(username):
        return json({'error': 'Username already exists'}, status=409)

    user_id = str(uuid.uuid4())
    user = User(user_id)
    user.username = username
    user.password = body['password']

    inserted_id = _db.add_user(user)
    if not inserted_id:
        raise ApiInternalError('Failed to register user')

    return json({'message': 'User registered successfully'}, status=201)


@users_bp.route('/login', methods=['POST'])
@validate_with_jsonschema(login_json_schema)
async def login_user(request):
    body = request.json
    username = body['username']
    password = body['password']

    user_data = _db.get_user_by_username(username)
    if not user_data or user_data['password'] != password:
        return json({'error': 'Invalid credentials'}, status=401)

    token = generate_jwt(username, role=user_data.get('role', 'user'))

    return json({
        "message": "Login successful",
        "token": token
    })


