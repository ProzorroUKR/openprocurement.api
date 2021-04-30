from schematics.types import StringType, MD5Type
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from openprocurement.api.models import Model, Value
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.core.procedure.models.document import PostDocument, Document
from openprocurement.tender.core.procedure.models.base import (
    ListType,
    PatchBusinessOrganization,
    PostBusinessOrganization,
)
from openprocurement.tender.pricequotation.procedure.models.req_response import RequirementResponse
from openprocurement.tender.pricequotation.validation import _validate_requirement_responses
from openprocurement.tender.pricequotation.procedure.validation import validate_bid_value
from uuid import uuid4


class PatchBid(Model):
    value = ModelType(Value)
    tenderers = ListType(ModelType(PatchBusinessOrganization, required=True), min_size=1, max_size=1)
    status = StringType(choices=["active", "draft"])

    def validate_value(self, data, value):
        if value is not None:
            tender = get_tender()
            validate_bid_value(tender, value)


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
    status = StringType(choices=["active", "draft"], default="active")
    value = ModelType(Value)
    documents = ListType(ModelType(PostDocument, required=True), default=list)
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
        criterion = tender['criteria']
        _validate_requirement_responses(criterion, value)


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
    status = StringType(choices=["active", "draft"])
    value = ModelType(Value)
    requirementResponses = ListType(
        ModelType(RequirementResponse),
        required=True,
        min_size=1,
    )
