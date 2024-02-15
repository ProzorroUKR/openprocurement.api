from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import OPERATIONS


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


# contract
def validate_contract_update_with_accepted_complaint(request, **_):
    tender = request.validated["tender"]
    award_id = request.validated["contract"].get("awardID", "")

    for award in tender.get("awards", []):
        if award["id"] == award_id:
            for complaint in award.get("complaints", []):
                if complaint.get("status", "") == "accepted":
                    raise_operation_error(request, "Can't update contract with accepted complaint")


# Contract documents
def validate_contract_document_complaints(operation):
    def validate(request, **_):
        for award in request.validated["tender"].get("awards", []):
            if award["id"] == request.validated["contract"]["awardID"]:
                for complaint in award.get("complaints", []):
                    if complaint["status"] == "accepted":
                        raise_operation_error(request, f"Can't {operation} document with accepted complaint")

    return validate
