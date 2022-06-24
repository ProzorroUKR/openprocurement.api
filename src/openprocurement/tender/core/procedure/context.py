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


def get_tender() -> Union[dict, None]:
    tender = thread_context.request.validated.get("tender")
    return tender


def get_contract() -> Union[dict, None]:
    tender = thread_context.request.validated.get("contract")
    return tender


def get_bid() -> dict:
    bid = thread_context.request.validated.get("bid")
    return bid


def get_document() -> dict:
    return thread_context.request.validated.get("document")


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


def get_bids_before_auction_results_context():
    """
    get_bids_before_auction_results
    we need it for each lot, so we set it on first call
    and use it multiple times for one request
    """
    if "bids_before_auction" not in thread_context.request.validated:
        tender = thread_context.request.validated["tender"]
        from openprocurement.tender.core.procedure.awarding import get_bids_before_auction_results
        thread_context.request.validated["bids_before_auction"] = get_bids_before_auction_results(tender)
    return thread_context.request.validated["bids_before_auction"]
