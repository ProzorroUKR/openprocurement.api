from openprocurement.tender.core.procedure.validation import (
    validate_item_operation_in_disallowed_tender_statuses,
)


def unless_selection_bot(*validations):
    def decorated(request, **_):
        if request.authenticated_role != "agreement_selection":
            for validation in validations:
                validation(request)

    return decorated


# lot
validate_lot_operation_in_disallowed_tender_statuses = validate_item_operation_in_disallowed_tender_statuses(
    "lot",
    ("active.enquiries", "draft"),
)
