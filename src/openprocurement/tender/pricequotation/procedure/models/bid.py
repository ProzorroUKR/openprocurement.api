from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import MD5Type, StringType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.value import Value
from openprocurement.api.procedure.types import ListType
from openprocurement.api.validation import validate_items_uniq
from openprocurement.tender.core.procedure.models.bid_document import (
    Document,
    PostDocument,
)
from openprocurement.tender.core.procedure.models.item import BaseItem
from openprocurement.tender.core.procedure.models.organization import (
    BusinessOrganization,
)
from openprocurement.tender.core.procedure.models.req_response import (
    MatchResponseValue,
    ObjResponseMixin,
    PatchObjResponsesMixin,
    PostBidResponsesMixin,
)
from openprocurement.tender.pricequotation.procedure.models.req_response import (
    RequirementResponse,
)
from openprocurement.tender.pricequotation.procedure.validation import (
    validate_bid_value,
)


def validate_requirement_responses(criterias, req_responses):
    requirements = {
        r["id"]: r for c in criterias for g in c.get("requirementGroups", "") for r in g.get("requirements", "")
    }
    expected_ids = set(requirements.keys())
    actual_ids = {r["requirement"]["id"] for r in req_responses}
    if len(actual_ids) != len(req_responses):
        raise ValidationError('Duplicate references for criterias')

    diff = expected_ids - actual_ids
    if diff:
        raise ValidationError(f'Missing references for criterias: {list(diff)}')

    additional = actual_ids - expected_ids
    if additional:
        raise ValidationError(f'No such criteria with id {additional}')


class PatchBid(PatchObjResponsesMixin, Model):
    value = ModelType(Value)
    tenderers = ListType(ModelType(BusinessOrganization, required=True), min_size=1, max_size=1)
    status = StringType(
        choices=["draft", "pending", "active", "invalid", "invalid.pre-qualification", "unsuccessful", "deleted"],
    )
    items = ListType(ModelType(BaseItem, required=True))

    def validate_value(self, data, value):
        if value is not None:
            tender = get_tender()
            validate_bid_value(tender, value)


class PostBid(PostBidResponsesMixin, PatchBid):
    @serializable
    def id(self):
        return uuid4().hex

    tenderers = ListType(ModelType(BusinessOrganization, required=True), required=True, min_size=1, max_size=1)
    value = ModelType(Value)
    documents = ListType(ModelType(PostDocument, required=True))
    requirementResponses = ListType(
        ModelType(RequirementResponse),
        required=True,
        min_size=1,
    )
    status = StringType(
        choices=["draft", "pending", "active", "invalid", "invalid.pre-qualification", "unsuccessful", "deleted"],
        default="draft",
    )
    items = ListType(
        ModelType(BaseItem, required=True),
        min_size=1,
        validators=[validate_items_uniq],
    )

    def validate_value(self, data, value):
        tender = get_tender()
        validate_bid_value(tender, value)

    def validate_requirementResponses(self, data, value):
        tender = get_tender()
        criterion = tender.get("criteria", [])
        validate_requirement_responses(criterion, value)
        for response in value:
            MatchResponseValue.match(response)
        super().validate_requirementResponses(self, data, value)


class Bid(ObjResponseMixin, Model):
    id = MD5Type()
    date = StringType()
    owner = StringType()
    owner_token = StringType()
    transfer_token = StringType()
    documents = ListType(ModelType(Document, required=True))
    financialDocuments = ListType(ModelType(Document, required=True))
    eligibilityDocuments = ListType(ModelType(Document, required=True))
    qualificationDocuments = ListType(ModelType(Document, required=True))

    tenderers = ListType(ModelType(BusinessOrganization, required=True), required=True, min_size=1, max_size=1)
    value = ModelType(Value)
    requirementResponses = ListType(
        ModelType(RequirementResponse),
        required=True,
        min_size=1,
    )
    status = StringType(
        choices=["draft", "pending", "active", "invalid", "invalid.pre-qualification", "unsuccessful", "deleted"],
        required=True,
    )
    items = ListType(
        ModelType(BaseItem, required=True),
        min_size=1,
        validators=[validate_items_uniq],
    )

    def validate_requirementResponses(self, data, value):
        tender = get_tender()
        criterion = tender.get("criteria", [])
        validate_requirement_responses(criterion, value)
        for response in value:
            MatchResponseValue.match(response)
        super().validate_requirementResponses(self, data, value)
