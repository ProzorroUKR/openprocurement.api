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


# award document
def validate_accepted_complaints(request, **kwargs):
    award_lot = request.validated["award"].get("lotID")
    if any(
        any(c.get("status") == "accepted" for c in i.get("complaints", ""))
        for i in request.validated["tender"].get("awards", "")
        if i.get("lotID") == award_lot
    ):
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} document with accepted complaint",
        )


# Contract documents
def validate_contract_document_complaints(operation):
    def validate(request, **_):
        for award in request.validated["tender"].get("awards", []):
            if award["id"] == request.validated["contract"]["awardID"]:
                for complaint in award.get("complaints", []):
                    if complaint["status"] == "accepted":
                        raise_operation_error(request, f"Can't {operation} document with accepted complaint")
    return validate
