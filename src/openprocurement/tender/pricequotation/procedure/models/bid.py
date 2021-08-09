from schematics.types import StringType, MD5Type
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable
from openprocurement.api.models import Model, Value
from openprocurement.api.validation import OPERATIONS
from openprocurement.api.utils import raise_operation_error
from openprocurement.tender.core.procedure.context import get_tender, get_request
from openprocurement.tender.core.procedure.models.bid import get_default_bid_status
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

    def validate_tenderers(self, _, value):
        if value and value[0].identifier:
            tenderer_id = value[0].identifier.id
            if tenderer_id and tenderer_id not in (
                i["identifier"]["id"]
                for i in get_tender().get("shortlistedFirms", "")
            ):
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
    status = StringType(choices=["active", "draft"], required=True)
    value = ModelType(Value)
    requirementResponses = ListType(
        ModelType(RequirementResponse),
        required=True,
        min_size=1,
    )
