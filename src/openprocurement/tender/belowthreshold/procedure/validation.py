from openprocurement.api.constants import GUARANTEE_ALLOWED_TENDER_TYPES
from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import OPERATIONS
from openprocurement.tender.core.procedure.validation import (
    validate_item_operation_in_disallowed_tender_statuses,
)


# BID DOCUMENTS
def validate_bid_document_operation_in_not_allowed_tender_status(request, **_):
    tender = request.validated["tender"]
    if tender["status"] == "active.awarded" and tender["procurementMethodType"] in GUARANTEE_ALLOWED_TENDER_TYPES:
        bid_id = request.validated["bid"]["id"]
        if all(
            award["status"] not in ("pending", "active") and award["bid_id"] == bid_id
            for award in tender.get("awards", "")
        ):
            raise_operation_error(
                request,
                f"Can't {OPERATIONS.get(request.method)} document " f"in current ({tender['status']}) tender status",
            )
    elif tender["status"] not in ("active.tendering", "active.qualification"):
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} document " f"in current ({tender['status']}) tender status",
        )


# tender documents
def validate_document_operation_in_not_allowed_period(request, **_):
    tender_status = request.validated["tender"]["status"]
    if (
        request.authenticated_role != "auction"
        and tender_status
        not in (
            "draft",
            "active.enquiries",
            "active.tendering",
        )
        or request.authenticated_role == "auction"
        and tender_status not in ("active.auction", "active.qualification")
    ):
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} document in current ({tender_status}) tender status",
        )


# lot
validate_lot_operation_in_disallowed_tender_statuses = validate_item_operation_in_disallowed_tender_statuses(
    "lot",
    ("active.enquiries", "draft"),
)
