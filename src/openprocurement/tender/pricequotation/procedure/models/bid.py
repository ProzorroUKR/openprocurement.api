from schematics.types import StringType, MD5Type
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from openprocurement.tender.core.procedure.context import get_tender, get_request
from openprocurement.api.context import get_now
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
        raise ValidationError('Duplicate references for criterias')

    diff = expected_ids - actual_ids
    if diff and get_first_revision_date(get_tender(), default=get_now()) > PQ_CRITERIA_RESPONSES_ALL_FROM:
        raise ValidationError(f'Missing references for criterias: {list(diff)}')

    additional = actual_ids - expected_ids
    if additional:
        raise ValidationError(f'No such criteria with id {additional}')

    for response in req_responses:
        response_id = response["requirement"]["id"]

        MatchResponseValue.match(requirements[response_id], response)


class MatchResponseValue:

    @classmethod
    def _match_expected_value(cls, datatype, requirement, value):
        expected_value = requirement.get("expectedValue")
        if expected_value:
            expected_value = datatype.to_native(expected_value)
            if datatype.to_native(expected_value) != value:
                raise ValidationError(f"Value \"{value}\" does not match expected value \"{expected_value}\" "
                                      f"in requirement {requirement['id']}")

    @classmethod
    def _match_min_max_value(cls, datatype, requirement, value):
        min_value = requirement.get('minValue')
        max_value = requirement.get('maxValue')

        if min_value and value < datatype.to_native(min_value):
            raise ValidationError(f"Value {value} is lower then minimal required {min_value} "
                                  f"in requirement {requirement['id']}")
        if max_value and value > datatype.to_native(max_value):
            raise ValidationError(f"Value {value} is higher then required {max_value} "
                                  f"in requirement {requirement['id']}")

    @classmethod
    def _match_expected_values(cls, datatype, requirement, values):
        expected_min_items = requirement.get("expectedMinItems")
        expected_max_items = requirement.get("expectedMaxItems")
        expected_values = requirement.get("expectedValues", [])
        expected_values = {datatype.to_native(i) for i in expected_values}

        if expected_min_items and expected_min_items > len(values):
            raise ValidationError(f"Count of items lower then minimal required {expected_min_items} "
                                  f"in requirement {requirement['id']}")

        if expected_max_items and expected_max_items < len(values):
            raise ValidationError(f"Count of items higher then maximum required {expected_max_items} "
                                  f"in requirement {requirement['id']}")

        if not set(values).issubset(set(expected_values)):
            raise ValidationError(f"Values isn't in requirement {requirement['id']}")

    @classmethod
    def match(cls, requirement, response):
        datatype = TYPEMAP[requirement['dataType']]

        value = response.get("value")
        values = response.get("values")

        if value is None and not values:
            raise ValidationError('response required at least one of field ["value", "values"]')
        if value is not None and values:
            raise ValidationError("field 'value' conflicts with 'values'")

        if value is not None:
            value = datatype.to_native(response['value'])
            field_for_value = ('expectedValue', 'minValue', 'maxValue')
            if all(i not in requirement for i in field_for_value):
                raise ValidationError(f"field 'value' is rogue without one of fields: {field_for_value} "
                                      f"in requirement({requirement['id']})")
            cls._match_expected_value(datatype, requirement, value)
            cls._match_min_max_value(datatype, requirement, value)

        elif values is not None:
            if 'expectedValues' not in requirement:
                raise ValidationError(f"field 'values' is rogue without 'expectedValues' field "
                                      f"in requirement({requirement['id']})")
            values = [datatype.to_native(v) for v in values]
            cls._match_expected_values(datatype, requirement, values)


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
