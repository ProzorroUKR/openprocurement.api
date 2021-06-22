# -*- coding: utf-8 -*-
from schematics.exceptions import ValidationError

from openprocurement.api.utils import error_handler, raise_operation_error
from openprocurement.api.validation import\
    validate_data, OPERATIONS, validate_json_data
from openprocurement.tender.pricequotation.utils import\
    responses_to_tree, criteria_to_tree
from openprocurement.tender.core.validation import TYPEMAP
from openprocurement.framework.core.design import agreements_search_contracts


# tender documents
def validate_document_operation_in_not_allowed_period(request, **kwargs):
    if request.validated["tender_status"] not in ["active.tendering", "draft"]:
        raise_operation_error(
            request,
            "Can't {} document in current ({}) tender status".format(
                OPERATIONS.get(request.method), request.validated["tender_status"]
            ),
        )


# award
def validate_create_award_not_in_allowed_period(request, **kwargs):
    tender = request.validated["tender"]
    if tender.status != "active.qualification":
        raise_operation_error(
            request,
            "Can't create award in current ({}) tender status".format(
                tender.status
            )
        )


def validate_award_update_in_terminal_status(request, **kwargs):
    award_status = request.validated['award'].status
    if award_status in ('cancelled', 'unsuccessful'):
        raise_operation_error(
            request,
            "Can't update award in current ({}) status".format(
                award_status
            )
        )


# contract document
def validate_contract_document_operation(request, **kwargs):
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


def validate_patch_tender_data(request, **kwargs):
    model = type(request.tender)
    data = validate_data(request, model, True, validate_json_data(request))
    _validate_kind_update(request, model)
    return data


def _validate_kind_update(request, model):
    data = request.validated["data"]
    kind = data.get("procuringEntity", {}).get("kind", "")
    if kind and kind not in model.procuring_entity_kinds:
        request.errors.add(
            "body", "kind",
            "{kind!r} procuringEntity cannot publish this type of procedure. Only {kinds} are allowed.".format(
                kind=kind, kinds=", ".join(model.procuring_entity_kinds)
            )
        )
        request.errors.status = 403


def _validate_bid_value(tender, value):
    if not value:
        raise ValidationError("This field is required.")
    if tender.value.amount < value.amount:
        raise ValidationError("value of bid should be less than value of tender")
    if tender.get("value").currency != value.currency:
        raise ValidationError("currency of bid should be identical to currency of value of tender")
    if tender.get("value").valueAddedTaxIncluded != value.valueAddedTaxIncluded:
        raise ValidationError(
            "valueAddedTaxIncluded of bid should be identical " "to valueAddedTaxIncluded of value of tender"
        )


def validate_post_bid(request, **kwargs):
    bid = request.validated["bid"]
    tender = request.validated["tender"]
    tenderer_id = bid["tenderers"][0]["identifier"]["id"]
    if tenderer_id not in [i.identifier.id for i in tender.shortlistedFirms]:
        raise_operation_error(request, f"Can't add bid if tenderer not in shortlistedFirms")


def _validate_requirement_responses(criterias, req_responses):
    criterias = criteria_to_tree(criterias)
    responses = responses_to_tree(req_responses)
    # top level criterias. all required
    diff = set(criterias).difference(responses)
    if diff:
        raise ValidationError('Missing references for criterias: {}'.format(
            list(diff)
        ))

    for criteria_id, group_response in responses.items():
        # OR for requirementGroup
        if len(group_response) > 1:
            raise ValidationError(
                'Provided groups {} conflicting in criteria {}'.format(
                    list(group_response.keys()), criteria_id
                ))
        criteria_groups = criterias.get(criteria_id, {})
        if not criteria_groups:
            raise ValidationError('No such criteria with id {}'.format(criteria_id))
        for group_id, requirements in criteria_groups.items():
            if group_id not in group_response:
                continue
            # response satisfies requirement
            responses = group_response.get(group_id, set())
            diff = set(requirements).difference(responses)
            if diff:
                raise ValidationError(
                    'Missing references for reqirements: {}'.format(
                        list(diff)
                    ))
            for response_id, response in responses.items():
                _matches(requirements[response_id], response)


def _matches(criteria, response):
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
                'Value "{}" does not match expected value "{}" in reqirement {}'.format(
                    value, expected, criteria['id']
                )
            )
    if min_value and max_value:
        min_value = datatype.to_native(min_value)
        max_value = datatype.to_native(max_value)
        if value < min_value or value > max_value:
            raise ValidationError(
                'Value "{}" does not match range from "{}" to "{}" in reqirement {}'.format(
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
                'Value {} is lower then minimal required {} in reqirement {}'.format(
                    value,
                    min_value,
                    criteria['id']
                )
            )
    if not min_value and max_value:
        if value > datatype.to_native(max_value):
            raise ValidationError(
                'Value {} is higher then required {} in reqirement {}'.format(
                    value,
                    max_value,
                    criteria['id']
                )
            )
    return response


def validate_tender_publish(request, **kwargs):
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
