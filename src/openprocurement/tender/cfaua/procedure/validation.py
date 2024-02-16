from openprocurement.api.utils import raise_operation_error
from openprocurement.api.validation import OPERATIONS
from openprocurement.tender.cfaua.procedure.models.tender import (
    LOTS_MAX_SIZE,
    LOTS_MIN_SIZE,
)


# award
def validate_update_award_in_not_allowed_status(request, **_):
    status = request.validated["tender"]["status"]
    if status not in ("active.qualification", "active.qualification.stand-still"):
        raise_operation_error(request, f"Can't update award in current ({status}) tender status")


def validate_award_document_tender_not_in_allowed_status(request, **_):
    if request.authenticated_role == "bots":
        allowed_tender_statuses = (
            "active.awarded",
            "active.qualification.stand-still",
            "active.qualification",
        )
    else:
        allowed_tender_statuses = ("active.qualification",)

    status = request.validated["tender"]["status"]
    if status not in allowed_tender_statuses:
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} document in current ({status}) tender status",
        )


# lot
def validate_lot_count(request, **_):
    lots_count = len(request.validated["tender"].get("lots", ""))

    if request.method == "DELETE" and lots_count <= LOTS_MIN_SIZE:
        raise_operation_error(request, f"Lots count in tender cannot be less than {LOTS_MAX_SIZE} items")

    elif request.method == "POST" and lots_count >= LOTS_MAX_SIZE:
        raise_operation_error(request, f"Lots count in tender cannot be more than {LOTS_MAX_SIZE} items")
