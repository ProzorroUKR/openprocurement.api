from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import OPERATIONS
from openprocurement.tender.core.procedure.utils import is_item_owner


def validate_post_bid_status(request, **_):
    bid_status = request.validated["data"].get("status")
    allowed = ("draft", "pending")
    if bid_status and bid_status not in allowed:
        raise_operation_error(request, f"Bid can be added only with status: {allowed}.")


def validate_view_bids(request, **_):
    tender_status = request.validated["tender"]["status"]
    if tender_status == "active.tendering":
        raise_operation_error(
            request,
            "Can't view {} in current ({}) tender status".format(
                "bid" if request.matchdict.get("bid_id") else "bids", tender_status
            ),
        )


def validate_bid_status_update_not_to_pending(request, **_):
    if request.authenticated_role != "Administrator":
        bid_status_to = request.validated["json_data"].get("status")
        bid_status_from = request.validated["bid"].get("status")
        if bid_status_from == bid_status_to:
            return
        if bid_status_to and bid_status_to != "pending":
            raise_operation_error(request, "Can't update bid to ({}) status".format(bid_status_to))


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
