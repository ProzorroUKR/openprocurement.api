import logging

from aiohttp.helpers import BasicAuth
from aiohttp.web import HTTPUnauthorized, middleware
from pydantic import BaseModel

from openprocurement.api.auth import DEFAULT_ACCRS, read_auth_users

logger = logging.getLogger(__name__)


class User(BaseModel):
    name: str = "anonymous"
    level: str = "anonymous"
    group: str = "anonymous"
    role: str | None = None


def login_user(request, users, allow_anonymous=True):
    authorization = request.headers.get("Authorization")
    error_text = "Authorization not found"
    if authorization:
        error_text = "Authorization invalid"
        if authorization.startswith("Bearer "):
            auth_token = authorization.split(" ")[-1]
        else:
            try:
                auth = BasicAuth.decode(authorization)
            except ValueError as e:
                raise HTTPUnauthorized(text=e.args[0])
            else:
                # FIXME: Use auth.password instead of auth.login
                # Brokers now using username instead of password
                # We need 2 step migration to use password instead of username
                auth_token = auth.login

        user_info = users.get(auth_token)
        if user_info:
            return User(name=user_info["name"], group=user_info["group"], level=user_info["level"])

    if allow_anonymous:
        return User()
    else:
        raise HTTPUnauthorized(text=error_text)


def get_login_middleware(auth_file):
    users = read_auth_users(auth_file, encoding="utf8", default_level=DEFAULT_ACCRS)

    @middleware
    async def login_middleware(request, handler):
        request.user = login_user(
            request,
            allow_anonymous=request.method in ("GET", "HEAD"),
            users=users,
        )
        response = await handler(request)
        return response

    return login_middleware
