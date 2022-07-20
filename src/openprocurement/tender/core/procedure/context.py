from openprocurement.api.constants import TZ
from openprocurement.api.context import get_now, set_now, set_request, get_request, get_data, get_json_data
from datetime import datetime
from typing import Union
import threading

# monkey.patch_all() makes this gevent._gevent_clocal.local instance
thread_context = threading.local()


def get_tender() -> Union[dict, None]:
    tender = get_request().validated.get("tender")
    return tender


def get_contract() -> Union[dict, None]:
    tender = get_request().validated.get("contract")
    return tender


def get_bid() -> dict:
    bid = get_request().validated.get("bid")
    return bid


def get_document() -> dict:
    return get_request().validated.get("document")


def get_bids_before_auction_results_context():
    """
    get_bids_before_auction_results
    we need it for each lot, so we set it on first call
    and use it multiple times for one request
    """
    if "bids_before_auction" not in get_request().validated:
        tender = get_request().validated["tender"]
        from openprocurement.tender.core.procedure.awarding import get_bids_before_auction_results
        get_request().validated["bids_before_auction"] = get_bids_before_auction_results(tender)
    return get_request().validated["bids_before_auction"]
