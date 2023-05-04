import threading
from datetime import datetime
from typing import Union
from pyramid.request import Request
from openprocurement.api.constants import TZ

# monkey.patch_all() makes this gevent._gevent_clocal.local instance
thread_context = threading.local()


def get_request() -> Request:
    return getattr(thread_context, "request", None)


def set_request(request):
    thread_context.request = request


def get_json_data() -> Union[list, dict]:
    bid = thread_context.request.validated.get("json_data")
    return bid


def get_data() -> Union[list, dict]:
    bid = thread_context.request.validated.get("data")
    return bid


def set_now(now=None):
    """
    request time
    we set it once at the request begging and use everywhere
    """
    thread_context.now = now or datetime.now(TZ)


def get_now() -> datetime:
    return thread_context.now


def get_db_session() -> Request:
    return getattr(thread_context, "db_session", None)


def set_db_session(db_session):
    thread_context.db_session = db_session
