from openprocurement.tender.competitivedialogue.utils import (
    prepare_shortlistedFirms,
    prepare_bid_identifier,
)
from openprocurement.api.utils import raise_operation_error


def validate_firm_to_create_bid(request, **_):
    tender = request.validated["tender"]
    bid = request.validated["data"]
    firm_keys = prepare_shortlistedFirms(tender.get("shortlistedFirms") or "")
    bid_keys = prepare_bid_identifier(bid)
    if not (bid_keys <= firm_keys):
        raise_operation_error(request, "Firm can't create bid")
