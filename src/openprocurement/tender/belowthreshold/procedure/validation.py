from openprocurement.api.constants_env import BELOWTHRESHOLD_FUNDERS_IDS
from openprocurement.tender.core.procedure.validation import (
    validate_document_operation_in_allowed_tender_statuses,
    validate_item_operation_in_disallowed_tender_statuses,
    validate_tender_status_allows_update,
)


# tender
def tender_for_funder(tender):
    return tender.get("_id") in BELOWTHRESHOLD_FUNDERS_IDS


def validate_tender_status_allows_update_operation(request, **_):
    allowed_statuses = [
        "draft",
        "active.enquiries",
        "active.pre-qualification",  # state class only allows status change (pre-qualification.stand-still)
        "active.pre-qualification.stand-still",
    ]

    if tender_for_funder(request.validated["tender"]):
        allowed_statuses.append("active.tendering")

    validate_tender_status_allows_update(*allowed_statuses)(request, **_)


def validate_tender_document_operation_in_allowed_tender_statuses(request, **_):
    allowed_statuses = ["draft", "active.enquiries"]

    if tender_for_funder(request.validated["tender"]):
        allowed_statuses.append("active.tendering")

    validate_document_operation_in_allowed_tender_statuses(allowed_statuses)(request, **_)


# lot
validate_lot_operation_in_disallowed_tender_statuses = validate_item_operation_in_disallowed_tender_statuses(
    "lot",
    ("active.enquiries", "draft"),
)
