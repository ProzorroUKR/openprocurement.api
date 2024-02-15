from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import OPERATIONS
from openprocurement.tender.core.procedure.validation import (
    validate_item_operation_in_disallowed_tender_statuses,
)


def unless_selection_bot(*validations):
    def decorated(request, **_):
        if request.authenticated_role != "agreement_selection":
            for validation in validations:
                validation(request)

    return decorated


def validate_document_operation_in_not_allowed_period(request, **_):
    tender_status = request.validated["tender"]["status"]
    if (
        request.authenticated_role != "auction"
        and tender_status not in ("draft", "draft.pending", "active.enquiries")
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
