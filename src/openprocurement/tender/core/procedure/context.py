from openprocurement.api.constants import TZ
from datetime import datetime
import threading

# monkey.patch_all() makes this gevent._gevent_clocal.local instance
thread_context = threading.local()


def get_request():
    return thread_context.request


def set_request(request):
    thread_context.request = request


def get_tender():
    tender = thread_context.request.validated["tender"]
    return tender


def get_bid():
    bid = thread_context.request.validated.get("bid")
    return bid


def get_document():
    return thread_context.request.validated.get("document")


def get_json_data():
    bid = thread_context.request.validated.get("json_data")
    return bid


# request time
# we set it once at the request begging and use everywhere
def set_now(now=None):
    thread_context.now = now or datetime.now(TZ)


def get_now():
    return thread_context.now
