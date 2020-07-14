# -*- coding: utf-8 -*-
from schematics.types import DecimalType, StringType, IntType, BooleanType
from schematics.exceptions import ValidationError

from openprocurement.api.utils import error_handler, raise_operation_error
from openprocurement.api.validation import\
    validate_data, OPERATIONS, validate_json_data
from openprocurement.tender.pricequotation.utils import\
    responses_to_tree, criteria_to_tree


TYPEMAP = {
    'string': StringType(),
    'integer': IntType(),
    'number': DecimalType(),
    'boolean': BooleanType()
}


# tender documents
def validate_document_operation_in_not_allowed_period(request):
    if request.validated["tender_status"] not in ["active.tendering", "draft"]:
        raise_operation_error(
            request,
            "Can't {} document in current ({}) tender status".format(
                OPERATIONS.get(request.method), request.validated["tender_status"]
            ),
        )


# award
def validate_create_award_not_in_allowed_period(request):
    tender = request.validated["tender"]
    if tender.status != "active.qualification":
        raise_operation_error(
            request,
            "Can't create award in current ({}) tender status".format(
                tender.status
            )
        )


def validate_award_update_in_terminal_status(request):
    award_status = request.validated['award'].status
    if award_status in ('cancelled', 'unsuccessful'):
        raise_operation_error(
            request,
            "Can't update award in current ({}) status".format(
                award_status
            )
        )


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


def validate_award_document(request):
    operation = OPERATIONS.get(request.method)

    allowed_tender_statuses = ["active.qualification"]
    if request.authenticated_role == "bots":
        allowed_tender_statuses.append("active.awarded")
    if request.validated["tender_status"] not in allowed_tender_statuses:
        raise_operation_error(
            request,
            "Can't {} document in current ({}) tender status".format(
                operation, request.validated["tender_status"]
            ),
        )

    if operation == "update" and request.authenticated_role != (request.context.author or "tender_owner"):
        request.errors.add("url", "role", "Can update document only author")
        request.errors.status = 403
        raise error_handler(request.errors)


def validate_patch_tender_data(request):
    model = type(request.tender)
    data = validate_data(request, model, True, validate_json_data(request))
    validate_kind_update(request, model)
    return data


def validate_kind_update(request, model):
    data = request.validated["data"]
    kind = data.get("procuringEntity", {}).get("kind", "")
    if kind and kind not in model.procuring_entity_kinds:
        request.errors.add(
            "procuringEntity", "kind",
            "{kind!r} procuringEntity cannot publish this type of procedure. Only {kinds} are allowed.".format(
                kind=kind, kinds=", ".join(model.procuring_entity_kinds)
            )
        )
        request.errors.status = 403


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


# tender.criterion.requirementGrpoups
def validate_requirement_groups(value):
    for requirements in value:
        for requirement in requirements.requirements:
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
    min_value = criteria.get('minValue')
    max_value = criteria.get('maxValue')

    if expected:
        expected = datatype.to_native(expected)
        if datatype.to_native(expected) != value:
            raise ValidationError(
                u'Value "{}" does not match expected value "{}" in reqirement {}'.format(
                    value, expected, criteria['id']
                )
            )
    if min_value and max_value:
        min_value = datatype.to_native(min_value)
        max_value = datatype.to_native(max_value)
        if value < min_value or value > max_value:
            raise ValidationError(
                u'Value "{}" does not match range from "{}" to "{}" in reqirement {}'.format(
                    value,
                    min_value,
                    max_value,
                    criteria['id']
                )
            )

    if min_value and not max_value:
        min_value = datatype.to_native(min_value)
        if value < min_value:
            raise ValidationError(
                u'Value {} is lower then minimal required {} in reqirement {}'.format(
                    value,
                    min_value,
                    criteria['id']
                )
            )
    if not min_value and max_value:
        if value < min_value:
            raise ValidationError(
                u'Value {} is higher then required {} in reqirement {}'.format(
                    value,
                    max_value,
                    criteria['id']
                )
            )
    return response


def validate_requirement_responses(criterias, req_responses):
    criterias = criteria_to_tree(criterias)
    responses = responses_to_tree(req_responses)
    # top level criterias. all required
    diff = set(criterias).difference(responses)
    if diff:
        raise ValidationError(u'Missing references for criterias: {}'.format(
            list(diff)
        ))

    for criteria_id, group_response in responses.items():
        # OR for requirementGroup
        if len(group_response) > 1:
            raise ValidationError(
                u'Provided groups {} conflicting in criteria {}'.format(
                    group_response.keys(), criteria_id
                ))
        criteria_groups = criterias[criteria_id]
        for group_id, requirements in criteria_groups.items():
            if group_id not in group_response:
                continue
            # response satisfies requirement
            responses = group_response.get(group_id, set())
            diff = set(requirements).difference(responses)
            if diff:
                raise ValidationError(
                    u'Missing references for reqirements: {}'.format(
                        list(diff)
                    ))
            for response_id, response in responses.items():
                matches(requirements[response_id], response)


def validate_tender_publish(request):
    current_status = request.validated['tender'].status
    tender_status = request.validated['data'].get('status', current_status)
    if tender_status == current_status:
        return
    if request.authenticated_role not in ("bots", "Administrator", "chronograph") \
            and tender_status != "draft.publishing":
        raise_operation_error(request,
                              "{} can't switch tender from status ({}) to ({})".format(request.authenticated_role,
                                                                                       current_status,
                                                                                       tender_status))
