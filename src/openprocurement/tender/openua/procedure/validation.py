from openprocurement.tender.core.procedure.utils import is_item_owner
from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import OPERATIONS


def validate_download_bid_document(request, **_):
    if request.params.get("download"):
        document = request.validated["document"]
        if (
            document.get("confidentiality", "") == "buyerOnly"
            and request.authenticated_role not in ("aboveThresholdReviewers", "sas")
            and not is_item_owner(request, request.validated["bid"])
            and not is_item_owner(request, request.validated["tender"])
        ):
            raise_operation_error(request, "Document download forbidden.")


def validate_bid_document_in_tender_status(request, **_):
    """
    active.tendering - tendering docs
    active.awarded - qualification docs that should be posted into award (another temp solution)
    """
    status = request.validated["tender"]["status"]
    if status not in (
        "active.tendering",
        "active.qualification",  # multi-lot procedure may be in this status despite of the active award
        "active.awarded",
    ):
        operation = OPERATIONS.get(request.method)
        raise_operation_error(
            request,
            "Can't {} document in current ({}) tender status".format(operation, status)
        )


def validate_bid_document_operation_in_award_status(request, **_):
    if request.validated["tender"]["status"] in ("active.qualification", "active.awarded") and not any(
        award["status"] == "active" and award["bid_id"] == request.validated["bid"]["id"]
        for award in request.validated["tender"].get("awards", "")
    ):
        raise_operation_error(
            request,
            "Can't {} document because award of bid is not active".format(
                OPERATIONS.get(request.method)
            ),
        )


def validate_update_bid_document_confidentiality(request, **_):
    tender_status = request.validated["tender"]["status"]
    if tender_status != "active.tendering" and "confidentiality" in request.validated.get("data", {}):
        document = request.validated["document"]
        if document.get("confidentiality", "public") != request.validated["data"]["confidentiality"]:
            raise_operation_error(
                request,
                "Can't update document confidentiality in current ({}) tender status".format(tender_status),
            )
