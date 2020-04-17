# -*- coding: utf-8 -*-
from schematics.types import DecimalType, StringType, IntType, BooleanType
from schematics.exceptions import ValidationError

from openprocurement.api.constants import RELEASE_2020_04_19
from openprocurement.api.utils import error_handler, raise_operation_error, get_now, get_first_revision_date
from openprocurement.api.validation import validate_data, OPERATIONS, validate_json_data
from openprocurement.tender.pricequotation.utils import sort_by_id, reformat_criteria, reformat_response


TYPEMAP = {
    'string': StringType(),
    'integer': IntType(),
    'number': DecimalType(),
    'boolean': BooleanType()
}


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

# cancellation
def validate_create_cancellation_in_active_auction(request):
    tender = request.validated["tender"]
    tender_created = get_first_revision_date(tender, default=get_now())
    if tender_created > RELEASE_2020_04_19 and tender.status in ["active.auction"]:
        raise_operation_error(
            request, "Can't create cancellation in current ({}) tender status".format(tender.status))


# tender.criterion.requirementGrpoups
def validate_requirement_groups(value):
    for requirement in value:
        expected = requirement.get('expectedValue')
        min_value = requirement.get('minValue')
        max_value = requirement.get('maxValue')
        if not any((expected, min_value, max_value)):
            raise ValidationError(
                u'Value required for at least one field ["expectedValue", "minValue", "maxValue"]'
            )
        if any((expected and min_value, expected and max_value)):
            raise ValidationError(
                u'expectedValue conflicts with ["minValue", "maxValue"]'
            )


def validate_value_type(value, datatype):
    if not value:
        return
    type_ = TYPEMAP.get(datatype)
    if not type_:
        raise ValidationError(
            u'Type mismatch: value {} does not confront type {}'.format(
                value, type_
            )
        )
    # validate value
    type_.to_native(value)


# bid.requirementResponeses
def matches(criteria, response):
    datatype = TYPEMAP[criteria['dataType']]
    # validate value
    value = datatype.to_native(response['value'])

    expected = criteria.get('expectedValue')
    min_value = criteria.get('expectedValue')
    max_value = criteria.get('expectedValue')

    if expected:
        expected = datatype.to_native(expected)
        if datatype.to_native(expected) != value:
            raise ValidationError(
                u'Value {} does not match expected value {} in reqirement {}'.format(
                    str(value), str(expected), criteria['id']
                )
            )
    if min_value and max_value:
        min_value = datatype.to_native(min_value)
        max_value = datatype.to_native(max_value)
        if value < min_value or value > max_value:
            raise ValidationError(
                u'Value {} does not match range from {} to {} in reqirement {}'.format(
                    str(value), str(min_value), str(max_value), criteria['id']
                )
            )
            
    if min_value and not max_value:
        min_value = datatype.to_native(min_value)
        if value < min_value:
            raise ValidationError(
                u'Value {} is lower then minimal required {} in reqirement {}'.format(
                    str(value), str(min_value), criteria['id']
                )
            )
    if not min_value and max_value:
        if value < min_value:
            raise ValidationError(
                u'Value {} is higher then required {} in reqirement {}'.format(
                    str(value), str(max_value), criteria['id']
                )
            )


def validate_requirement_responses(criterias, req_responses):
    criterias = sort_by_id(reformat_criteria(criterias))
    req_responses = sort_by_id(reformat_response(req_responses))
    if len(criterias) != len(req_responses):
        raise ValidationError(u'Number of requitementResponeses ({}) does not match total number of reqirements ({})'.format(
            len(req_responses), len(criterias))
        )
    diff = set((c['id'] for c in criterias)).difference((r['id'] for r in req_responses))
    if diff:
        raise ValidationError(u'Mismatch keys in requirement_responses. Missing references: {}'.format(
            list(diff)
        ))

    for criteria, response in zip(criterias, req_responses):
        matches(criteria, response)
