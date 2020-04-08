# -*- coding: utf-8 -*-
from schematics.exceptions import ValidationError
from openprocurement.api.utils import error_handler, raise_operation_error, get_now
from openprocurement.api.validation import validate_data, OPERATIONS, validate_json_data


# tender documents
def validate_document_operation_in_not_allowed_tender_status(request):
    if request.validated["tender_status"] != "active.tendering":
        raise_operation_error(
            request,
            "Can't {} document in current ({}) tender status".format(
                OPERATIONS.get(request.method), request.validated["tender_status"]
            ),
        )


# bids
def validate_view_bids(request):
    if request.validated["tender_status"] in ["active.tendering"]:
        raise_operation_error(
            request,
            "Can't view {} in current ({}) tender status".format(
                "bid" if request.matchdict.get("bid_id") else "bids", request.validated["tender_status"]
            ),
        )




# award
def validate_create_award_not_in_allowed_period(request):
    tender = request.validated["tender"]
    if tender.status != "active.qualification":
        raise_operation_error(request, "Can't create award in current ({}) tender status".format(tender.status))


def validate_create_award_only_for_active_lot(request):
    tender = request.validated["tender"]
    award = request.validated["award"]
    if any([i.status != "active" for i in tender.lots if i.id == award.lotID]):
        raise_operation_error(request, "Can create award only in active lot status")


# contract document
def validate_contract_document(request):
    operation = OPERATIONS.get(request.method)
    if request.validated["tender_status"] not in\
       ["active.qualification", "active.awarded"]:
        raise_operation_error(
            request,
            "Can't {} document in current ({}) tender status".format(
                operation, request.validated["tender_status"]
            ),
        )
    if request.validated["contract"].status not in ["pending", "active"]:
        raise_operation_error(
            request,
            "Can't {} document in current contract status".format(operation)
        )
    return True


def validate_cancellation_document_operation_not_in_allowed_status(request):
    if request.validated["tender_status"] in ["complete", "cancelled", "unsuccessful"]:
        raise_operation_error(
            request,
            "Can't {} document in current ({}) tender status".format(
                OPERATIONS.get(request.method), request.validated["tender_status"]
            ),
        )


def validate_award_document(request):
    operation = OPERATIONS.get(request.method)

    allowed_tender_statuses = ["active.qualification"]
    if request.authenticated_role == "bots":
        allowed_tender_statuses.append("active.awarded")
    if request.validated["tender_status"] not in allowed_tender_statuses:
        raise_operation_error(
            request,
            "Can't {} document in current ({}) tender status".format(operation, request.validated["tender_status"]),
        )

    if operation == "update" and request.authenticated_role != (request.context.author or "tender_owner"):
        request.errors.add("url", "role", "Can update document only author")
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_patch_tender_data(request):
    data = validate_json_data(request)
    return validate_data(request, type(request.tender), True, data)


def validate_bid_value(tender, value):
    if not value:
        raise ValidationError(u"This field is required.")
    if tender.value.amount < value.amount:
        raise ValidationError(u"value of bid should be less than value of tender")
    if tender.get("value").currency != value.currency:
        raise ValidationError(u"currency of bid should be identical to currency of value of tender")
    if tender.get("value").valueAddedTaxIncluded != value.valueAddedTaxIncluded:
        raise ValidationError(
            u"valueAddedTaxIncluded of bid should be identical " u"to valueAddedTaxIncluded of value of tender"
        )
