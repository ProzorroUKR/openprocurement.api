from schematics.exceptions import ValidationError

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import error_handler
from openprocurement.tender.core.procedure.context import get_bid


def validation_error_handler(func):
    def wrapper(self, *args, **kwargs):
        try:
            func(self, *args, **kwargs)
        except ValidationError as e:
            if isinstance(e.messages, dict):
                error_name = list(e.messages[0].keys())[0]
                error_msg = e.messages[0][error_name]
            else:
                error_name = "data"
                error_msg = e.messages[0]

            self.request.errors.status = 422
            self.request.errors.add("body", error_name, error_msg)
            raise error_handler(self.request)

    return wrapper


def awarding_is_unsuccessful(awards):
    """
    Check whether awarding is unsuccessful for tender/lot.
    If hasAwardingOrder is True and hasMultiSourcing is False, then only the last award's status is being checked.
    If hasAwardingOrder is False, all awards are being checked. If there are no awards with statuses
    active or pending for tender/lot, then awarding is unsuccessful.
    """
    tender = get_tender()
    awarding_order_enabled = tender["config"]["hasAwardingOrder"]
    has_multi_sourcing = tender["config"].get("hasMultiSourcing")
    awards_statuses = {award["status"] for award in awards}
    if awarding_order_enabled is False or has_multi_sourcing:
        return not awards_statuses.intersection({"active", "pending"})
    return awards and awards[-1]["status"] == "unsuccessful"


def invalidate_pending_bid():
    bid = get_bid()
    tender = get_tender()
    if tender.get("status") == "active.tendering" and bid.get("status") == "pending":
        bid["status"] = "invalid"
