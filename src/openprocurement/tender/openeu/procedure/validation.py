from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import OPERATIONS
from openprocurement.tender.core.procedure.utils import is_item_owner


def validate_view_bid_document(request, **_):
    tender_status = request.validated["tender"]["status"]
    if tender_status == "active.tendering" and not is_item_owner(request, request.validated["bid"]):
        raise_operation_error(
            request,
            "Can't view bid documents in current ({}) tender status".format(tender_status),
        )


def validate_bid_document_operation_in_bid_status(request, **_):
    bid = request.validated["bid"]
    if bid["status"] in ("unsuccessful", "deleted"):
        raise_operation_error(
            request,
            "Can't {} document at '{}' bid status".format(
                OPERATIONS.get(request.method),
                bid["status"]
            )
        )


def validate_view_bid_documents_allowed_in_bid_status(request, **_):
    bid_status = request.validated["bid"]["status"]
    if bid_status in ("invalid", "deleted") and not is_item_owner(request, request.validated["bid"]):
        raise_operation_error(
            request,
            f"Can't view bid documents in current ({bid_status}) bid status"
        )


def validate_view_financial_bid_documents_allowed_in_tender_status(request, **_):
    tender_status = request.validated["tender"]["status"]
    view_forbidden_states = (
        "active.tendering",
        "active.pre-qualification",
        "active.pre-qualification.stand-still",
        "active.auction",
    )
    if tender_status in view_forbidden_states and not is_item_owner(request, request.validated["bid"]):
        raise_operation_error(
            request,
            f"Can't view bid documents in current ({tender_status}) tender status",
        )


def validate_view_financial_bid_documents_allowed_in_bid_status(request, **_):
    bid_status = request.validated["bid"]["status"]
    if bid_status in ("invalid", "deleted", "invalid.pre-qualification", "unsuccessful") \
       and not is_item_owner(request, request.validated["bid"]):
        raise_operation_error(
            request,
            f"Can't view bid documents in current ({bid_status}) bid status"
        )
