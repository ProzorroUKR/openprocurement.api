# -*- coding: utf-8 -*-
from openprocurement.api.validation import validate_data, OPERATIONS
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.api.utils import (
    update_logging_context,
    error_handler,
    get_now,
    raise_operation_error,
    get_revision_changes,
    get_first_revision_date,
)  # XXX tender context
from openprocurement.tender.core.utils import apply_patch
from openprocurement.tender.core.validation import (
    validate_complaint_accreditation_level,
    validate_cancellation_status_with_complaints,
    validate_cancellation_status_without_complaints,
)


def validate_complaint_data(request):
    update_logging_context(request, {"complaint_id": "__new__"})
    validate_complaint_accreditation_level(request)
    model = type(request.context).complaints.model_class
    return validate_data(request, model)


def validate_patch_complaint_data(request):
    model = type(request.context.__parent__).complaints.model_class
    return validate_data(request, model, True)


# tender
def validate_chronograph(request):
    if request.authenticated_role == "chronograph":
        raise_operation_error(request, "Chronograph has no power over me!")


def validate_chronograph_before_2020_04_19(request):
    tender = request.validated["tender"]
    if get_first_revision_date(tender, default=get_now()) < RELEASE_2020_04_19:
        validate_chronograph(request)


def validate_update_tender_with_awards(request):
    tender = request.validated["tender"]

    if tender.awards and request.authenticated_role != "chronograph":
        raise_operation_error(request, "Can't update tender when there is at least one award.")


# tender document
def validate_operation_with_document_not_in_active_status(request):
    if request.validated["tender_status"] != "active":
        raise_operation_error(
            request,
            "Can't {} document in current ({}) tender status".format(
                OPERATIONS.get(request.method), request.validated["tender_status"]
            ),
        )


# lot
def validate_lot_operation_not_in_active_status(request):
    tender = request.validated["tender"]
    if tender.status != "active":
        raise_operation_error(
            request, "Can't {} lot in current ({}) tender status".format(OPERATIONS.get(request.method), tender.status)
        )


def validate_lot_operation_with_awards(request):
    tender = request.validated["tender"]
    if tender.awards:
        raise_operation_error(
            request, "Can't {} lot when you have awards".format(OPERATIONS.get(request.method), tender.status)
        )


# award
def validate_award_operation_not_in_active_status(request):
    tender = request.validated["tender"]
    if tender.status != "active":
        raise_operation_error(
            request,
            "Can't {} award in current ({}) tender status".format(
                "create" if request.method == "POST" else "update", tender.status
            ),
        )


def validate_create_new_award(request):
    tender = request.validated["tender"]
    if tender.awards and tender.awards[-1].status in ["pending", "active"]:
        raise_operation_error(
            request, "Can't create new award while any ({}) award exists".format(tender.awards[-1].status)
        )


def validate_lot_cancellation(request):

    tender = request.validated["tender"]

    new_rules = get_first_revision_date(tender, default=get_now()) > RELEASE_2020_04_19

    if new_rules:
        return

    award = request.validated["award"]
    if (
        tender.get("lots")
        and tender.get("cancellations")
        and [
            cancellation
            for cancellation in tender.get("cancellations", [])
            if cancellation.get("relatedLot") == award.lotID
        ]
    ):
        raise_operation_error(
            request,
            "Can't {} award while cancellation for corresponding lot exists".format(OPERATIONS.get(request.method)),
        )


def validate_create_new_award_with_lots(request):
    tender = request.validated["tender"]
    award = request.validated["award"]
    if tender.awards:
        if tender.lots:  # If tender with lots
            if award.lotID in [aw.lotID for aw in tender.awards if aw.status in ["pending", "active"]]:
                raise_operation_error(
                    request,
                    "Can't create new award on lot while any ({}) award exists".format(tender.awards[-1].status),
                )
        else:
            validate_create_new_award(request)


# award document
def validate_document_operation_not_in_active(request):
    if request.validated["tender_status"] != "active":
        raise_operation_error(
            request,
            "Can't {} document in current ({}) tender status".format(
                OPERATIONS.get(request.method), request.validated["tender_status"]
            ),
        )


def validate_award_document_add_not_in_pending(request):
    if request.validated["award"].status != "pending":
        raise_operation_error(
            request, "Can't add document in current ({}) award status".format(request.validated["award"].status)
        )


# award complaint
def validate_award_complaint_operation_not_in_active(request):
    tender = request.validated["tender"]
    if tender.status != "active":
        raise_operation_error(
            request,
            "Can't {} complaint in current ({}) tender status".format(OPERATIONS.get(request.method), tender.status),
        )


# cancellation
def validate_absence_complete_lots_on_tender_cancel(request):
    tender = request.validated["tender"]
    cancellation = request.validated["cancellation"]
    if tender.lots and not cancellation.relatedLot:
        for lot in tender.lots:
            if lot.status == "complete":
                raise_operation_error(
                    request,
                    "Can't perform cancellation, if there is at least one complete lot"
                )


def validate_cancellation_status(request):
    tender = request.validated["tender"]
    cancellation = request.validated["cancellation"]

    lotID = cancellation.get("relatedLot")

    if (
        (not lotID and any(i for i in tender.awards if i.status == "active"))
        or (lotID and any(i for i in tender.awards if i.status == "active" and i.get("lotID") == lotID))
    ):
        validate_cancellation_status_with_complaints(request)
    else:
        validate_cancellation_status_without_complaints(request)


# contract
def validate_contract_operation_not_in_active(request):
    if request.validated["tender_status"] not in ["active"]:
        raise_operation_error(
            request,
            "Can't {} contract in current ({}) tender status".format(
                OPERATIONS.get(request.method), request.validated["tender_status"]
            ),
        )


def validate_contract_update_in_cancelled(request):
    if request.context.status == "cancelled":
        raise_operation_error(request, "Can't update contract in current ({}) status".format(request.context.status))


def validate_contract_with_cancellations_and_contract_signing(request):
    data = request.validated["data"]
    tender = request.validated["tender"]
    new_rules = get_first_revision_date(tender, default=get_now()) > RELEASE_2020_04_19

    if request.context.status != "active" and "status" in data and data["status"] == "active":

        award = [a for a in tender.awards if a.id == request.context.awardID][0]
        if (
            tender.get("lots")
            and tender.get("cancellations")
            and [
                cancellation
                for cancellation in tender.get("cancellations")
                if (
                    cancellation.get("relatedLot") == award.lotID
                    and cancellation.status not in ["unsuccessful"]
                )
            ]
        ):
            raise_operation_error(request, "Can't update contract while cancellation for corresponding lot exists")
        stand_still_end = award.complaintPeriod.endDate
        if stand_still_end > get_now():
            raise_operation_error(
                request, "Can't sign contract before stand-still period end ({})".format(stand_still_end.isoformat())
            )
        if (
            any(
                [
                    i.status in tender.block_complaint_status and a.lotID == award.lotID
                    for a in tender.awards
                    for i in a.complaints
                ]
            )
            or (
                new_rules
                and any([
                    i.status in tender.block_complaint_status and c.relatedLot == award.lotID
                    for c in tender.cancellations
                    for i in c.get("complaints")
                ])
            )
        ):
            raise_operation_error(request, "Can't sign contract before reviewing all complaints")


def validate_contract_items_count_modification(request):
    # as it is alowed to set/change contract.item.unit.value we need to
    # ensure that nobody is able to add or delete contract.item
    data = request.validated["data"]
    if data.get("items") and len(data["items"]) != len(request.context["items"]):
        request.errors.add("body", "data", "Can't change items count")
        request.errors.status = 403
        raise error_handler(request.errors)


# contract document
def validate_contract_document_operation_not_in_allowed_contract_status(request):
    contract = request.validated["contract"]
    if contract.status not in ["pending", "active"]:
        raise_operation_error(
            request, "Can't {} document in current contract status".format(OPERATIONS.get(request.method))
        )
