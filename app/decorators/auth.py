from functools import wraps
import jwt

from config import Config
from app.hooks.error import ApiUnauthorized


def check_token(request):
    token = request.token
    if not token:
        return False, None

    try:
        jwt_ = jwt.decode(
            token, Config.SECRET_KEY, algorithms=["HS256"]
        )
        return True, jwt_
    except jwt.exceptions.InvalidTokenError:
        return False, None


def protected(wrapped):
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            is_authenticated, jwt_ = check_token(request)

            if is_authenticated:
                kwargs['username'] = jwt_['username']
                response = await f(request, *args, **kwargs)
                return response
            else:
                raise ApiUnauthorized("You are unauthorized.")

        return decorated_function

    return decorator(wrapped)

from functools import wraps
from app.hooks.error import ApiUnauthorized

def check_owner(get_owner_username):
    def decorator(f):
        @wraps(f)
        async def wrapper(request, *args, **kwargs):
            current_user = kwargs.get("username")
            if not current_user:
                raise ApiUnauthorized("Missing authenticated user")

            owner_username = await get_owner_username(request, *args, **kwargs)
            print("check", owner_username)
            if owner_username != current_user:
                raise ApiUnauthorized("You are not the owner of this resource.")

            return await f(request, *args, **kwargs)
        return wrapper
    return decorator
