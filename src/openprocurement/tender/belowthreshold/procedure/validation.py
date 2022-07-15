from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import OPERATIONS
from openprocurement.api.constants import GUARANTEE_ALLOWED_TENDER_TYPES
from openprocurement.tender.core.procedure.validation import validate_item_operation_in_disallowed_tender_statuses


# BID DOCUMENTS
def validate_bid_document_operation_in_not_allowed_tender_status(request, **_):
    tender = request.validated["tender"]
    if tender["status"] == "active.awarded" and tender["procurementMethodType"] in GUARANTEE_ALLOWED_TENDER_TYPES:
        bid_id = request.validated["bid"]["id"]
        if not any(
            award["status"] in ("pending", "active") and award["bid_id"] == bid_id
            for award in tender.get("awards", "")
        ):
            raise_operation_error(
                request,
                f"Can't {OPERATIONS.get(request.method)} document "
                f"in current ({tender['status']}) tender status"
            )
    elif tender["status"] not in ("active.tendering", "active.qualification"):
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} document "
            f"in current ({tender['status']}) tender status"
        )


def validate_bid_document_operation_with_not_pending_award(request, **kwargs):
    tender = request.validated["tender"]
    bid = request.validated["bid"]
    if tender["status"] == "active.qualification" and not any(
        award["bid_id"] == bid["id"] and award["status"] in ("pending", "active")
        for award in tender.get("awards", "")
    ):
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} document because award of bid is not in pending state",
        )


def validate_upload_documents_not_allowed_for_simple_pmr(request, **kwargs):
    tender = request.validated["tender"]
    statuses = ("active.qualification",)
    if tender["status"] in statuses and tender.get("procurementMethodRationale") == "simple":
        bid_id = request.validated["bid"]["id"]
        bid_with_active_award = any(
            award["status"] == "active" and award["bid_id"] == bid_id
            for award in tender.get("awards", "")
        )
        needed_criterion = any(
            criterion["classification"]["id"] == "CRITERION.OTHER.CONTRACT.GUARANTEE"
            for criterion in tender.get("criteria", "")
        )
        if not all([needed_criterion, bid_with_active_award]):
            raise_operation_error(
                request,
                f"Can't upload document with {statuses} tender status and procurementMethodRationale simple"
            )


# tender documents
def validate_document_operation_in_not_allowed_period(request, **_):
    tender_status = request.validated["tender"]["status"]
    if (
        request.authenticated_role != "auction" and tender_status not in ("draft", "active.enquiries")
        or request.authenticated_role == "auction" and tender_status not in ("active.auction", "active.qualification")
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
