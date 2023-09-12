from openprocurement.tender.esco.procedure.state.tender import ESCOTenderStateMixin
from openprocurement.tender.core.procedure.state.complaint import ComplaintState
from openprocurement.tender.core.constants import (
    COMPLAINT_MIN_AMOUNT,
    COMPLAINT_ENHANCED_AMOUNT_RATE,
    COMPLAINT_ENHANCED_MIN_AMOUNT,
    COMPLAINT_ENHANCED_MAX_AMOUNT,
)
from openprocurement.tender.core.utils import restrict_value_to_bounds
from openprocurement.tender.esco.utils import get_bid_identifier, all_bids_values
from openprocurement.api.utils import (
    get_uah_amount_from_value,
    raise_operation_error,
)
from openprocurement.api.auth import extract_access_token
from logging import getLogger

LOGGER = getLogger(__name__)


class ESCOComplaintMixin(ESCOTenderStateMixin):
    request: object
    get_related_lot_obj: callable  # from tender.core.state.complaint.ComplaintState

    def get_complaint_amount(self, tender, complaint):
        if tender["status"] in ("active.tendering",
                                "active.pre-qualification",  # cancellation complaint
                                "active.pre-qualification.stand-still"):
            return COMPLAINT_MIN_AMOUNT
        else:
            # only bid owners can post complaints here
            acc_token = extract_access_token(self.request)
            for bid in tender.get("bids", ""):
                if bid["owner_token"] == acc_token:
                    value = self.helper_get_bid_value(tender, complaint, bid)
                    base_amount = get_uah_amount_from_value(
                        self.request, value, {"complaint_id": complaint["id"]}
                    )
                    amount = restrict_value_to_bounds(
                        base_amount * COMPLAINT_ENHANCED_AMOUNT_RATE,
                        COMPLAINT_ENHANCED_MIN_AMOUNT,
                        COMPLAINT_ENHANCED_MAX_AMOUNT
                    )
                    return amount
            else:  # never happens as acc_token must be in bids to allow complaint creation
                return raise_operation_error(
                    self.request, "Couldn't set a complaint value for an invalid bidder",
                )

    def helper_get_bid_value(self, tender, complaint, bid):
        if bid.get("lotValues"):  # check if it's a multi-lot
            identifier = get_bid_identifier(bid)
            lot = self.get_related_lot_obj(tender, complaint)
            if lot:  # if it's a lot related complaint, we look for the first related lotValue
                # we expect that a tenderer can have only one lotValue for a specific lot
                for lot_value in all_bids_values(tender, identifier):
                    if lot_value["relatedLot"] == lot["id"]:
                        return lot_value["value"]

            # if bidders complaint about something they don't relate
            # OR it's a whole tender related complaint (not lot)
            # we should sum all bidder amounts
            sum_value = dict(amount=0, currency="UAH")
            for lot_value in all_bids_values(tender, identifier):
                value = lot_value["value"]
                sum_value["amount"] += value["amount"]
                sum_value["currency"] = value["currency"]
            return sum_value
        else:
            return bid["value"]


class ESCOComplaintState(ESCOComplaintMixin, ComplaintState):
    pass
