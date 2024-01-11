from typing import Union
from openprocurement.api.context import get_request


def get_tender() -> Union[dict, None]:
    tender = get_request().validated.get("tender")
    return tender


def get_tender_config() -> Union[dict, None]:
    tender_config = get_request().validated.get("tender_config", {})
    return tender_config


def get_award() -> Union[dict, None]:
    award = get_request().validated.get("award")
    return award


def get_contract() -> Union[dict, None]:
    contract = get_request().validated.get("contract")
    return contract


def get_contract_config() -> Union[dict, None]:
    contract_config = get_request().validated.get("contract_config")
    return contract_config


def get_cancellation() -> Union[dict, None]:
    cancellation = get_request().validated.get("cancellation")
    return cancellation


def get_bid() -> dict:
    bid = get_request().validated.get("bid")
    return bid


def get_document() -> dict:
    return get_request().validated.get("document")


def get_complaint() -> dict:
    return get_request().validated.get("complaint")


def get_post() -> dict:
    return get_request().validated.get("post")


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
