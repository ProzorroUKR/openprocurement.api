# -*- coding: utf-8 -*-
from openprocurement.api.constants import CRITERION_REQUIREMENT_STATUSES_FROM
from openprocurement.api.utils import error_handler, raise_operation_error, get_first_revision_date, get_now
from openprocurement.api.validation import OPERATIONS, _validate_tender_first_revision_date
from openprocurement.tender.core.validation import (
    base_validate_operation_ecriteria_objects,
    _validate_related_criterion,
)


# tender documents
def validate_document_operation_in_not_allowed_tender_status(request, **kwargs):
    if (
        request.authenticated_role != "auction"
        and request.validated["tender_status"] not in ("draft", "active.enquiries")
        or request.authenticated_role == "auction"
        and request.validated["tender_status"] not in ("active.auction", "active.qualification")
    ):
        raise_operation_error(
            request,
            "Can't {} document in current ({}) tender status".format(
                OPERATIONS.get(request.method), request.validated["tender_status"]
            ),
        )


# bids
def validate_view_bids(request, **kwargs):
    if request.validated["tender_status"] in ["active.tendering", "active.auction"]:
        raise_operation_error(
            request,
            "Can't view {} in current ({}) tender status".format(
                "bid" if request.matchdict.get("bid_id") else "bids", request.validated["tender_status"]
            ),
        )


def validate_update_bid_status(request, **kwargs):
    if request.authenticated_role != "Administrator":
        bid_status_to = request.validated["data"].get("status")
        if bid_status_to != request.context.status and bid_status_to != "active":
            request.errors.add("body", "bid", "Can't update bid to ({}) status".format(bid_status_to))
            request.errors.status = 403
            raise error_handler(request)


# lot
def validate_lot_operation(request, **kwargs):
    tender = request.validated["tender"]
    if tender.status not in ("active.enquiries", "draft"):
        raise_operation_error(
            request, "Can't {} lot in current ({}) tender status".format(OPERATIONS.get(request.method), tender.status)
        )


def validate_delete_lot_related_criterion(request, **kwargs):
    lot_id = request.context.id
    _validate_related_criterion(request, lot_id, action="delete")


# complaint
def validate_add_complaint_not_in_allowed_tender_status(request, **kwargs):
    tender = request.context
    if tender.status not in ["active.enquiries",]:
        raise_operation_error(request, "Can't add complaint in current ({}) tender status".format(tender.status))


def validate_update_complaint_not_in_allowed_tender_status(request, **kwargs):
    tender = request.validated["tender"]
    if tender.status not in [
        "active.enquiries",
        "active.tendering",
        "active.auction",
        "active.qualification",
        "active.awarded",
    ]:
        raise_operation_error(request, "Can't update complaint in current ({}) tender status".format(tender.status))


def validate_submit_complaint_time(request, **kwargs):
    tender = request.validated["tender"]
    if get_now() > tender.enquiryPeriod.endDate:
        raise_operation_error(
            request,
            "Can submit complaint only in enquiryPeriod",
        )


def validate_update_complaint_not_in_allowed_status(request, **kwargs):
    if request.context.status not in ["draft", "claim", "answered"]:
        raise_operation_error(request, "Can't update complaint in current ({}) status".format(request.context.status))


# complaint document
def validate_complaint_document_operation_not_in_allowed_status(request, **kwargs):
    if request.validated["tender_status"] not in [
        "active.enquiries",
        "active.tendering",
        "active.auction",
        "active.qualification",
        "active.awarded",
    ]:
        raise_operation_error(
            request,
            "Can't {} document in current ({}) tender status".format(
                OPERATIONS.get(request.method), request.validated["tender_status"]
            ),
        )


def validate_role_and_status_for_add_complaint_document(request, **kwargs):
    roles = request.content_configurator.allowed_statuses_for_complaint_operations_for_roles
    if request.context.status not in roles.get(request.authenticated_role, []):
        raise_operation_error(
            request, "Can't add document in current ({}) complaint status".format(request.context.status)
        )


# auction
def validate_auction_info_view(request, **kwargs):
    if request.validated["tender_status"] != "active.auction":
        raise_operation_error(
            request, "Can't get auction info in current ({}) tender status".format(request.validated["tender_status"])
        )


# award
def validate_create_award_not_in_allowed_period(request, **kwargs):
    tender = request.validated["tender"]
    if tender.status != "active.qualification":
        raise_operation_error(request, "Can't create award in current ({}) tender status".format(tender.status))


def validate_create_award_only_for_active_lot(request, **kwargs):
    tender = request.validated["tender"]
    award = request.validated["award"]
    if any([i.status != "active" for i in tender.lots if i.id == award.lotID]):
        raise_operation_error(request, "Can create award only in active lot status")


# award complaint
def validate_award_complaint_update_not_in_allowed_status(request, **kwargs):
    if request.context.status not in ["draft", "claim", "answered"]:
        raise_operation_error(request, "Can't update complaint in current ({}) status".format(request.context.status))


# contract document
def validate_cancellation_document_operation_not_in_allowed_status(request, **kwargs):
    if request.validated["tender_status"] in ["complete", "cancelled", "unsuccessful"]:
        raise_operation_error(
            request,
            "Can't {} document in current ({}) tender status".format(
                OPERATIONS.get(request.method), request.validated["tender_status"]
            ),
        )


def validate_award_document(request, **kwargs):
    operation = OPERATIONS.get(request.method)

    allowed_tender_statuses = ["active.qualification"]
    if request.authenticated_role == "bots":
        allowed_tender_statuses.append("active.awarded")
    if request.validated["tender_status"] not in allowed_tender_statuses:
        raise_operation_error(
            request,
            "Can't {} document in current ({}) tender status".format(operation, request.validated["tender_status"]),
        )

    if any(
        [i.status != "active" for i in request.validated["tender"].lots if i.id == request.validated["award"].lotID]
    ):
        raise_operation_error(request, "Can {} document only in active lot status".format(operation))
    if operation == "update" and request.authenticated_role != (request.context.author or "tender_owner"):
        request.errors.add("url", "role", "Can update document only author")
        request.errors.status = 403
        raise error_handler(request)


def validate_operation_ecriteria_objects(request, **kwargs):
    valid_statuses = ["draft", "active.enquiries"]
    base_validate_operation_ecriteria_objects(request, valid_statuses)


def validate_change_requirement_objects(request, **kwargs):
    valid_statuses = ["draft"]
    tender = request.validated["tender"]
    tender_creation_date = get_first_revision_date(tender, default=get_now())
    if tender_creation_date < CRITERION_REQUIREMENT_STATUSES_FROM:
        valid_statuses.append("active.enquiries")
    base_validate_operation_ecriteria_objects(request, valid_statuses)


def validate_put_requirement_objects(request, **kwargs):
    _validate_tender_first_revision_date(request, validation_date=CRITERION_REQUIREMENT_STATUSES_FROM)
    valid_statuses = ["active.enquiries"]
    base_validate_operation_ecriteria_objects(request, valid_statuses)


def validate_upload_documents_not_allowed_for_simple_pmr(request, **kwargs):
    tender = request.validated["tender"]
    statuses = ("active.qualification",)
    if tender["status"] in statuses and tender.get("procurementMethodRationale") == "simple":
        if tender.get("procurementMethodRationale") == "simple":
            bid_id = request.validated["bid"]["id"]
            criteria = tender["criteria"]
            awards = tender["awards"]
            bid_with_active_award = any([award["status"] == "active" and award["bid_id"] == bid_id for award in awards])
            needed_criterion = any(
                [criterion["classification"]["id"] == "CRITERION.OTHER.CONTRACT.GUARANTEE" for criterion in criteria]
            )
            if not all([needed_criterion, bid_with_active_award]):
                raise_operation_error(
                    request,
                    "Can't upload document with {} tender status and procurementMethodRationale simple".format(
                        statuses
                    ),
                )
