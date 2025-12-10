from contextvars import ContextVar
from datetime import datetime
from typing import Any

from aiohttp.web import Request

from openprocurement.api.constants import ROUTE_PREFIX, TZ

request_id_var = ContextVar("request_id")
request_var = ContextVar("request_var")
request_logging_var = ContextVar("request_logging_var")
now_var = ContextVar("now_var")


def get_request_async() -> Request:
    return request_var.get()


def set_request_async(request: Request):
    request_var.set(request)


def get_request_logging_context(extra: dict[str, Any] = None):
    params = request_logging_var.get()
    if extra:
        params.update(extra)
    return params


def set_request_logging_context(params: dict[str, Any]):
    request_logging_var.set(params)


def url_to_absolute(url, add_prefix: bool = True):
    request = get_request_async()
    application_url = getattr(request, "application_url", "http://localhost")
    prefix = ROUTE_PREFIX if add_prefix else ""
    return application_url + prefix + url


def set_now_async():
    now_var.set(datetime.now(tz=TZ))


def get_now_async() -> datetime:
    return now_var.get()


def get_view_url(view_name: str, **kwargs: Any) -> str:
    router = get_request_async().app.router
    base_url = str(router[view_name].url_for(**kwargs))
    return base_url.removeprefix(ROUTE_PREFIX)
