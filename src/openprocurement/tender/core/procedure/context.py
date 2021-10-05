from openprocurement.api.constants import TZ
from datetime import datetime
from pyramid.request import Request
from typing import Union
import threading

# monkey.patch_all() makes this gevent._gevent_clocal.local instance
thread_context = threading.local()


def get_request() -> Request:
    return thread_context.request


def set_request(request):
    thread_context.request = request


def get_tender() -> dict:
    tender = thread_context.request.validated["tender"]
    return tender


def get_bid() -> dict:
    bid = thread_context.request.validated.get("bid")
    return bid


def get_document() -> dict:
    return thread_context.request.validated.get("document")


def get_json_data() -> Union[list, dict]:
    bid = thread_context.request.validated.get("json_data")
    return bid


# request time
# we set it once at the request begging and use everywhere
def set_now(now=None):
    thread_context.now = now or datetime.now(TZ)


def get_now() -> datetime:
    return thread_context.now
