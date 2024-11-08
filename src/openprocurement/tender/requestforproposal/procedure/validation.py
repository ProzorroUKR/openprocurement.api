from openprocurement.tender.core.procedure.validation import (
    validate_item_operation_in_disallowed_tender_statuses,
)

# lot
validate_lot_operation_in_disallowed_tender_statuses = validate_item_operation_in_disallowed_tender_statuses(
    "lot",
    ("active.enquiries", "draft"),
)
