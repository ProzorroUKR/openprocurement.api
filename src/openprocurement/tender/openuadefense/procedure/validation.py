from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import OPERATIONS


def validate_bid_document_operation_in_award_status(request, **_):
    if request.validated["tender"]["status"] in ("active.qualification", "active.awarded") and not any(
        award["status"] in ("pending", "active") and award["bid_id"] == request.validated["bid"]["id"]
        for award in request.validated["tender"].get("awards", "")
    ):
        raise_operation_error(
            request,
            "Can't {} document because award of bid is not in pending or active state".format(
                OPERATIONS.get(request.method)
            ),
        )
