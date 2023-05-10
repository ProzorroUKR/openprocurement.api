# -*- coding: utf-8 -*-
from openprocurement.api.utils import raise_operation_error, get_now
from openprocurement.api.validation import OPERATIONS


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


# award complaint
def validate_award_complaint_update_not_in_allowed_status(request, **kwargs):
    if request.context.status not in ["draft", "claim", "answered"]:
        raise_operation_error(request, "Can't update complaint in current ({}) status".format(request.context.status))
