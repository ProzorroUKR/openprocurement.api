# -*- coding: utf-8 -*-
from openprocurement.api.utils import get_now, raise_operation_error, get_first_revision_date
from openprocurement.api.constants import RELEASE_2020_04_19


def validate_qualification_update_with_cancellation_lot_pending(request, **kwargs):
    tender = request.validated["tender"]
    tender_created = get_first_revision_date(tender, default=get_now())
    qualification = request.validated["qualification"]
    lot_id = qualification.lotID

    if tender_created < RELEASE_2020_04_19 or not lot_id:
        return

    accept_lot = all([
        any([j.status == "resolved" for j in i.complaints])
        for i in tender.cancellations
        if i.status == "unsuccessful" and getattr(i, "complaints", None) and i.relatedLot == lot_id
    ])

    if (
        request.authenticated_role == "tender_owner"
        and (
            any([
                i for i in tender.cancellations
                if i.relatedLot and i.status == "pending" and i.relatedLot == lot_id])
            or not accept_lot
        )
    ):
        raise_operation_error(
            request,
            "Can't update qualification with pending cancellation lot",
        )


# qualification complaint
def validate_qualification_update_not_in_pre_qualification(request, **kwargs):
    tender = request.validated["tender"]
    if tender.status not in ["active.pre-qualification"]:
        raise_operation_error(request, "Can't update qualification in current ({}) tender status".format(tender.status))


def validate_cancelled_qualification_update(request, **kwargs):
    if request.context.status == "cancelled":
        raise_operation_error(request, "Can't update qualification in current cancelled qualification status")


def validate_add_complaint_not_in_pre_qualification(request, **kwargs):
    tender = request.validated["tender"]
    if tender.status not in ["active.pre-qualification.stand-still"]:
        raise_operation_error(request, "Can't add complaint in current ({}) tender status".format(tender.status))


def validate_update_complaint_not_in_pre_qualification(request, **kwargs):
    tender = request.validated["tender"]
    if tender.status not in ["active.pre-qualification", "active.pre-qualification.stand-still"]:
        raise_operation_error(request, "Can't update complaint in current ({}) tender status".format(tender.status))


def validate_update_qualification_complaint_only_for_active_lots(request, **kwargs):
    tender = request.validated["tender"]
    if any([i.status != "active" for i in tender.lots if i.id == request.validated["qualification"].lotID]):
        raise_operation_error(request, "Can update complaint only in active lot status")


def validate_add_complaint_not_in_qualification_period(request, **kwargs):
    tender = request.validated["tender"]
    if tender.qualificationPeriod and (
        tender.qualificationPeriod.startDate
        and tender.qualificationPeriod.startDate > get_now()
        or tender.qualificationPeriod.endDate
        and tender.qualificationPeriod.endDate < get_now()
    ):
        raise_operation_error(request, "Can add complaint only in qualificationPeriod")
