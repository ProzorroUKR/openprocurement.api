from openprocurement.tender.core.procedure.context import get_now
from openprocurement.tender.core.procedure.utils import get_first_revision_date
from openprocurement.tender.core.procedure.validation import validate_update_contract_status_base
from openprocurement.api.utils import raise_operation_error
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.api.validation import OPERATIONS


# award
def validate_award_operation_not_in_active_status(request, **kwargs):
    status = request.validated["tender"]["status"]
    if status != "active":
        raise_operation_error(
            request,
            f"Can't {'create' if request.method == 'POST' else 'update'} award in current ({status}) tender status"
        )


def validate_create_new_award(request, **kwargs):
    tender = request.validated["tender"]
    if tender.get("awards"):
        last_status = tender["awards"][-1]["status"]
        if last_status in ["pending", "active"]:
            raise_operation_error(
                request, f"Can't create new award while any ({last_status}) award exists"
            )


def validate_lot_cancellation(request, **kwargs):
    tender = request.validated["tender"]
    new_rules = get_first_revision_date(tender, default=get_now()) > RELEASE_2020_04_19
    if new_rules:
        return

    award = request.validated.get("award", request.validated["data"])
    lot_id = award.get("lotID")
    if (
        tender.get("lots")
        and tender.get("cancellations")
        and [
            cancellation
            for cancellation in tender.get("cancellations", [])
            if cancellation.get("relatedLot") == lot_id
        ]
    ):
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} award while cancellation for corresponding lot exists",
        )


def validate_create_new_award_with_lots(request, **kwargs):
    tender = request.validated["tender"]
    award = request.validated["data"]
    if tender.get("awards"):
        if tender.get("lots"):  # If tender with lots
            lot_id = award.get("lotID")
            if any(
                lot_id == aw.get("lotID")
                for aw in tender["awards"]
                if aw["status"] in ["pending", "active"]
            ):
                last_award_status = tender["awards"][-1]["status"]
                raise_operation_error(
                    request,
                    f"Can't create new award on lot while any ({last_award_status}) award exists",
                )
        else:
            validate_create_new_award(request, **kwargs)


def validate_award_same_lot_id(request, **kwargs):
    tender = request.validated["tender"]
    award = request.validated["data"]
    lot_id = award.get("lotID")
    if (
        lot_id and any(aw.get("lotID") == lot_id and aw["id"] != award["id"]
                       for aw in tender.get("awards")
                       if aw["status"] in ("pending", "active"))
    ):
        raise_operation_error(
            request,
            "Another award is already using this lotID.",
            location="body",
            name="lotID",
        )


# award document
def validate_document_operation_not_in_active(request, **kwargs):
    status = request.validated["tender"]["status"]
    if status != "active":
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} document in current ({status}) tender status",
        )


def validate_award_document_add_not_in_pending(request, **kwargs):
    status = request.validated["award"]["status"]
    if status != "pending":
        raise_operation_error(
            request,
            f"Can't add document in current ({status}) award status",
        )


# tender documents
def validate_document_operation_in_not_allowed_tender_status(request, **_):
    tender_status = request.validated["tender"]["status"]
    if tender_status not in ("draft", "active"):
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} document in current ({tender_status}) tender status",
        )


# contract
def validate_contract_update_in_cancelled(request, **_):
    if request.validated["contract"]["status"] == "cancelled":
        raise_operation_error(request, f"Can't update contract in current (cancelled) status")


def validate_contract_operation_not_in_active(request, **_):
    if request.validated["tender"]["status"] != "active":
        raise_operation_error(
            request,
            f"Can't {OPERATIONS.get(request.method)} contract in current "
            f"({request.validated['tender']['status']}) tender status"
        )


def validate_contract_items_count_modification(request, **_):
    # as it is alowed to set/change contract.item.unit.value we need to
    # ensure that nobody is able to add or delete contract.item
    data = request.validated["data"]
    if data.get("items") and len(data["items"]) != len(request.validated["contract"].get("items", [])):
        raise_operation_error(
            request,
            "Can't change items count"
        )


def validate_update_contract_status(request, **_):
    allowed_statuses_from = ("pending",)
    allowed_statuses_to = ("active",)
    validate_update_contract_status_base(
        request,
        allowed_statuses_from,
        allowed_statuses_to
    )


# contract document
def validate_contract_document_operation_not_in_allowed_contract_status(operation):
    def validate(request, **_):
        if request.validated["contract"]["status"] not in {"pending", "active"}:
            raise_operation_error(
                request, f"Can't {operation} document in current contract status"
            )
    return validate
