from typing import Union
from openprocurement.api.context import get_request
from openprocurement.api.procedure.context import get_object


def get_award() -> Union[dict, None]:
    return get_object("award")


def get_cancellation() -> Union[dict, None]:
    return get_object("cancellation")


def get_bid() -> dict:
    return get_object("bid")


def get_document() -> dict:
    return get_object("document")


def get_complaint() -> dict:
    return get_object("complaint")


def get_post() -> dict:
    return get_object("post")


def get_bids_before_auction_results_context():
    """
    get_bids_before_auction_results
    we need it for each lot, so we set it on first call
    and use it multiple times for one request
    """
    if "bids_before_auction" not in get_request().validated:
        tender = get_request().validated["tender"]
        from openprocurement.tender.core.procedure.utils import get_bids_before_auction_results
        get_request().validated["bids_before_auction"] = get_bids_before_auction_results(tender)
    return get_request().validated["bids_before_auction"]
