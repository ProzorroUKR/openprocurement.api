# -*- coding: utf-8 -*-
from openprocurement.api.utils import get_now, raise_operation_error, get_first_revision_date
from openprocurement.api.validation import validate_data, OPERATIONS
from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.tender.openeu.models import Qualification


def validate_qualification_update_with_cancellation_lot_pending(request):
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


def validate_patch_qualification_data(request):
    return validate_data(request, Qualification, True)


# bids
def validate_view_bids_in_active_tendering(request):
    if request.validated["tender_status"] == "active.tendering":
        raise_operation_error(
            request,
            "Can't view {} in current ({}) tender status".format(
                "bid" if request.matchdict.get("bid_id") else "bids", request.validated["tender_status"]
            ),
        )


# bid documents
def validate_bid_document_operation_in_bid_status(request):
    bid = request.validated["bid"]
    if bid.status in ("invalid", "unsuccessful", "deleted"):
        raise_operation_error(
            request,
            "Can't {} document at '{}' bid status".format(
                OPERATIONS.get(request.method),
                bid.status
            )
        )


def validate_view_bid_documents_allowed_in_tender_status(request):
    tender_status = request.validated["tender_status"]
    if tender_status == "active.tendering" and request.authenticated_role != "bid_owner":
        raise_operation_error(
            request,
            "Can't view bid documents in current ({}) tender status".format(tender_status),
        )


def validate_view_financial_bid_documents_allowed_in_tender_status(request):
    tender_status = request.validated["tender_status"]
    view_forbidden_states = (
        "active.tendering",
        "active.pre-qualification",
        "active.pre-qualification.stand-still",
        "active.auction",
    )
    if tender_status in view_forbidden_states and request.authenticated_role != "bid_owner":
        raise_operation_error(
            request,
            "Can't view bid documents in current ({}) tender status".format(tender_status),
        )


def validate_view_bid_documents_allowed_in_bid_status(request):
    bid_status = request.validated["bid"].status
    if bid_status in ("invalid", "deleted") and request.authenticated_role != "bid_owner":
        raise_operation_error(
            request,
            "Can't view bid documents in current ({}) bid status".format(bid_status)
        )


def validate_view_financial_bid_documents_allowed_in_bid_status(request):
    bid_status = request.validated["bid"].status
    if bid_status in ("invalid", "deleted", "invalid.pre-qualification", "unsuccessful") \
       and request.authenticated_role != "bid_owner":
        raise_operation_error(
            request,
            "Can't view bid documents in current ({}) bid status".format(bid_status)
        )


# qualification
def validate_qualification_document_operation_not_in_allowed_status(request):
    if request.validated["tender_status"] != "active.pre-qualification":
        raise_operation_error(
            request,
            "Can't {} document in current ({}) tender status".format(
                OPERATIONS.get(request.method), request.validated["tender_status"]
            ),
        )


def validate_qualification_document_operation_not_in_pending(request):
    qualification = request.validated["qualification"]
    if qualification.status != "pending":
        raise_operation_error(
            request, "Can't {} document in current qualification status".format(OPERATIONS.get(request.method))
        )


# qualification complaint
def validate_qualification_update_not_in_pre_qualification(request):
    tender = request.validated["tender"]
    if tender.status not in ["active.pre-qualification"]:
        raise_operation_error(request, "Can't update qualification in current ({}) tender status".format(tender.status))


def validate_cancelled_qualification_update(request):
    if request.context.status == "cancelled":
        raise_operation_error(request, "Can't update qualification in current cancelled qualification status")


def validate_add_complaint_not_in_pre_qualification(request):
    tender = request.validated["tender"]
    if tender.status not in ["active.pre-qualification.stand-still"]:
        raise_operation_error(request, "Can't add complaint in current ({}) tender status".format(tender.status))


def validate_update_complaint_not_in_pre_qualification(request):
    tender = request.validated["tender"]
    if tender.status not in ["active.pre-qualification", "active.pre-qualification.stand-still"]:
        raise_operation_error(request, "Can't update complaint in current ({}) tender status".format(tender.status))


def validate_update_qualification_complaint_only_for_active_lots(request):
    tender = request.validated["tender"]
    if any([i.status != "active" for i in tender.lots if i.id == request.validated["qualification"].lotID]):
        raise_operation_error(request, "Can update complaint only in active lot status")


def validate_add_complaint_not_in_qualification_period(request):
    tender = request.validated["tender"]
    if tender.qualificationPeriod and (
        tender.qualificationPeriod.startDate
        and tender.qualificationPeriod.startDate > get_now()
        or tender.qualificationPeriod.endDate
        and tender.qualificationPeriod.endDate < get_now()
    ):
        raise_operation_error(request, "Can add complaint only in qualificationPeriod")
