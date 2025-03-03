from openprocurement.tender.core.procedure.validation import (
    validate_document_operation_in_allowed_tender_statuses,
    validate_item_operation_in_disallowed_tender_statuses,
)

# tender
validate_tender_document_operation_in_allowed_tender_statuses = validate_document_operation_in_allowed_tender_statuses(
    ("draft", "active.enquiries")
)

# lot
validate_lot_operation_in_disallowed_tender_statuses = validate_item_operation_in_disallowed_tender_statuses(
    "lot",
    ("active.enquiries", "active.tendering", "draft"),
)
