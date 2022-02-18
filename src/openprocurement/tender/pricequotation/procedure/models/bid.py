from schematics.types import StringType, MD5Type
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from openprocurement.tender.core.procedure.context import get_tender, get_request, get_now
from openprocurement.tender.core.procedure.models.bid import get_default_bid_status
from openprocurement.tender.core.procedure.models.document import PostDocument, Document
from openprocurement.tender.core.procedure.models.base import ListType
from openprocurement.tender.core.procedure.models.organization import (
    PatchBusinessOrganization,
    PostBusinessOrganization,
)
from schematics.exceptions import ValidationError
from openprocurement.api.models import Model, Value
from openprocurement.api.utils import raise_operation_error, get_first_revision_date
from openprocurement.api.constants import PQ_CRITERIA_RESPONSES_ALL_FROM
from openprocurement.api.validation import OPERATIONS
from openprocurement.tender.core.validation import TYPEMAP
from openprocurement.tender.pricequotation.procedure.models.req_response import RequirementResponse
from openprocurement.tender.pricequotation.procedure.validation import validate_bid_value
from uuid import uuid4


def validate_requirement_responses(criterias, req_responses):
    requirements = {r["id"]: r
                    for c in criterias
                    for g in c.get("requirementGroups", "")
                    for r in g.get("requirements", "")}
    expected_ids = set(requirements.keys())
    actual_ids = {r["requirement"]["id"] for r in req_responses}
    if len(actual_ids) != len(req_responses):
        raise ValidationError(f'Duplicate references for criterias')

    diff = expected_ids - actual_ids
    if diff and get_first_revision_date(get_tender(), default=get_now()) > PQ_CRITERIA_RESPONSES_ALL_FROM:
        raise ValidationError(f'Missing references for criterias: {list(diff)}')

    additional = actual_ids - expected_ids
    if additional:
        raise ValidationError(f'No such criteria with id {additional}')

    for response in req_responses:
        response_id = response["requirement"]["id"]
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


class PatchBid(Model):
    value = ModelType(Value)
    tenderers = ListType(ModelType(PatchBusinessOrganization, required=True), min_size=1, max_size=1)
    status = StringType(choices=["active", "draft"])

    def validate_value(self, data, value):
        if value is not None:
            tender = get_tender()
            validate_bid_value(tender, value)

    def validate_tenderers(self, _, value):
        if value and value[0].identifier:
            tenderer_id = value[0].identifier.id
            if tenderer_id and tenderer_id not in {
                i["identifier"]["id"]
                for i in get_tender().get("shortlistedFirms", "")
            }:
                # it's 403, not 422, so we can't raise ValueError or ValidationError
                request = get_request()
                raise_operation_error(request,
                                      f"Can't {OPERATIONS[request.method]} bid if tenderer not in shortlistedFirms")


class PostBid(PatchBid):
    @serializable
    def id(self):
        return uuid4().hex

    tenderers = ListType(
        ModelType(PostBusinessOrganization, required=True),
        required=True,
        min_size=1,
        max_size=1
    )
    status = StringType(choices=["active", "draft"], default=get_default_bid_status("active"))
    value = ModelType(Value)
    documents = ListType(ModelType(PostDocument, required=True))
    requirementResponses = ListType(
        ModelType(RequirementResponse),
        required=True,
        min_size=1,
    )

    def validate_value(self, data, value):
        tender = get_tender()
        validate_bid_value(tender, value)

    def validate_requirementResponses(self, data, value):
        tender = get_tender()
        criterion = tender.get("criteria", [])
        validate_requirement_responses(criterion, value)


class Bid(Model):
    id = MD5Type()
    date = StringType()
    owner = StringType()
    owner_token = StringType()
    transfer_token = StringType()
    documents = ListType(ModelType(Document, required=True))

    tenderers = ListType(
        ModelType(PostBusinessOrganization, required=True),
        required=True,
        min_size=1,
        max_size=1
    )
    status = StringType(choices=["active", "draft"], required=True)
    value = ModelType(Value)
    requirementResponses = ListType(
        ModelType(RequirementResponse),
        required=True,
        min_size=1,
    )

    def validate_requirementResponses(self, data, value):
        tender = get_tender()
        criterion = tender.get("criteria", [])
        validate_requirement_responses(criterion, value)
