import hashlib
import json
import logging
import time
import uuid
from base64 import b64decode

from aiohttp.web import HTTPException, HTTPInternalServerError, Request, Response
from aiohttp.web import json_response as base_json_response
from aiohttp.web import middleware
from bson.json_util import loads
from pydantic import ValidationError
from yarl import URL

from openprocurement.api.constants import JOURNAL_PREFIX
from openprocurement.api.constants_env import CRITICAL_HEADERS_LOG_ENABLED
from openprocurement.api.utils import json_dumps
from prozorro_cdb.api.context import (
    get_now_async,
    request_id_var,
    set_now_async,
    set_request_async,
    set_request_logging_context,
)
from prozorro_cdb.api.database.store import (
    get_mongodb,
    reset_db_session_async,
    set_db_session_async,
)
from prozorro_cdb.api.handlers.base import json_response_error

logger = logging.getLogger(__name__)


@middleware
async def error_middleware(request, handler):
    try:
        response = await handler(request)
    except ValidationError as exc:
        return json_response_error(
            exception=exc,
            context="Unknown",
        )
    except HTTPException as exc:
        if exc.content_type == "text/plain":
            exc.content_type = "application/json"
            exc.text = json_dumps(
                {
                    "type": "-".join(["http"] + exc.reason.lower().split(" ")),
                    "title": exc.reason,
                    "details": exc.text,
                    "status": exc.status_code,
                }
            )
        raise exc
    except Exception as exc:
        logger.exception(exc)
        raise HTTPInternalServerError(
            content_type="application/json",
            text=json_dumps(
                {
                    "type": "http-internal-server-error",
                    "title": "Internal Server Error",
                    "status": 500,
                }
            ),
        )
    return response


def json_response(*args, **kwargs):
    return base_json_response(dumps=json_dumps, *args, **kwargs)


@middleware
async def convert_response_to_json(request, handler):
    """
    convert dicts into valid json responses
    """
    response = await handler(request)
    if isinstance(response, dict):
        status_code = 201 if request.method in ("POST", "PUT") else 200
        response = json_response(response, status=status_code)
    return response


@middleware
async def jsonp_and_pretty_middleware(request, handler):
    response = await handler(request)

    pretty = request.query.get("opt_pretty")
    callback = request.query.get("opt_jsonp")
    if not pretty and not callback:
        return response

    # зчитуємо тіло JSON
    try:
        data = json.loads(response.text)
    except Exception:
        return response

    if pretty:
        body = json.dumps(data, ensure_ascii=False, indent=2)
    else:
        body = json.dumps(data, ensure_ascii=False, separators=(",", ":"))

    # --- параметр opt_jsonp=callback ---
    if callback:
        # JSONP обгортка
        body = f"/**/{callback}({body});"
        response = Response(
            text=body,
            content_type="application/javascript",
            status=response.status,
        )
    else:
        response = Response(
            text=body,
            content_type="application/json",
            status=response.status,
        )
    return response


def get_application_url(request: Request) -> str:
    """
    This method builds application_url for absolute urls.
    It translates HTTP_X_FORWARDED_ headers, as paste.deploy.config.PrefixMiddleware does.
    :return:
    """
    scheme = request.headers.get("X-Forwarded-Proto") or request.headers.get("X-Forwarded-Scheme") or request.scheme
    host = request.headers.get("X-Forwarded-Host") or request.headers.get("Host") or request.host
    if ":" in host:
        host, port = host.split(":", maxsplit=1)
        return str(URL.build(scheme=scheme, host=host, port=int(port)))
    return str(URL.build(scheme=scheme, host=host))


@middleware
async def context_middleware(request, handler):
    # set context variables
    request_id = request.headers.get("X-Client-Request-ID") or request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request_id_var.set(request_id)

    set_request_async(request)
    set_now_async()

    # set logging context
    user = getattr(request, "user", None)
    params = {
        f"{JOURNAL_PREFIX}API_VERSION": request.app["project_info"]["project"]["version"],
        f"{JOURNAL_PREFIX}TAGS": "python,api",
        f"{JOURNAL_PREFIX}USER": user and user.name,
        f"{JOURNAL_PREFIX}ROLE": user and user.role,
        f"{JOURNAL_PREFIX}PARAMS": str(dict(request.query)),
        f"{JOURNAL_PREFIX}CURRENT_URL": str(request.url),
        f"{JOURNAL_PREFIX}CURRENT_PATH": request.rel_url.path,
        f"{JOURNAL_PREFIX}REMOTE_ADDR": request.remote if hasattr(request, "remote") else "",
        f"{JOURNAL_PREFIX}USER_AGENT": request.headers.get("User-Agent", ""),
        f"{JOURNAL_PREFIX}REQUEST_METHOD": request.method,
        f"{JOURNAL_PREFIX}TIMESTAMP": get_now_async().isoformat(),
        f"{JOURNAL_PREFIX}REQUEST_ID": request.headers.get("X-Request-ID", request_id),
        f"{JOURNAL_PREFIX}CLIENT_REQUEST_ID": request.headers.get("X-Client-Request-ID", ""),
    }

    if CRITICAL_HEADERS_LOG_ENABLED:
        auth_header = request.headers.get("Authorization", "")
        params.update(
            {
                f"{JOURNAL_PREFIX}AUTHORIZATION": hashlib.md5(auth_header.encode()).hexdigest(),
                f"{JOURNAL_PREFIX}X_REQUEST_ID": request.headers.get("X-Request-ID", ""),
            }
        )

    # додати контекст до request
    set_request_logging_context(params)

    # application_url to build absolute urls
    request.application_url = get_application_url(request)

    # передати далі
    response = await handler(request)
    response.headers["X-Request-ID"] = request_id
    return response


access_logger = logging.getLogger("access")


@middleware
async def access_logger_middleware(request, handler):
    start_time = time.perf_counter()
    response = await handler(request)

    duration = time.perf_counter() - start_time
    remote_addr = request.remote or "-"
    user_identity = "-"
    user_name = "-"
    if user := getattr(request, "user", None):
        user_identity = user.role or "-"
        user_name = user.name
    now = get_now_async().strftime("%d/%b/%Y:%H:%M:%S %z")
    method = request.method
    path = request.rel_url
    version = f"HTTP/{request.version.major}.{request.version.minor}"
    status = getattr(response, "status", 500)
    length = getattr(response, "body", None)
    length = len(length) if length else "-"
    referer = request.headers.get("Referer", "-")
    user_agent = request.headers.get("User-Agent", "-")
    duration_str = f"{duration:.3f}"

    log_message = (
        f"{remote_addr} {user_identity} {user_name} [{now}] "
        f'"{method} {path} {version}" {status} {length} '
        f'"{referer}" "{user_agent}" {duration_str}'
    )
    logger.info(log_message)
    return response


@middleware
async def db_session_middleware(request, handler):
    """
    Sets db session contextvar
    :param request:
    :param handler:
    :return:
    """
    cookie_name = "SESSION"
    warning = None
    mongodb = get_mongodb()
    async with await mongodb.database.client.start_session(causal_consistency=True) as session:
        cookie = request.cookies.get(cookie_name)
        if cookie:
            try:
                values = loads(b64decode(cookie))
                session.advance_cluster_time(values["cluster_time"])  # global time in cluster level
                session.advance_operation_time(values["operation_time"])  # last successful operation time in session
            except Exception as exc:
                warning = f"Error on {cookie_name} cookie parsing: {exc}"
                logger.debug(warning)

        token = set_db_session_async(session)
        try:
            response = await handler(request)  # processing request
        finally:
            reset_db_session_async(token)

    if warning:
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Warning
        response.headers["X-Warning"] = f'199 - "{warning}"'

    return response
