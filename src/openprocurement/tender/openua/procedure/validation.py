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
