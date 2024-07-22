from uuid import uuid4

from schematics.types import StringType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.value import Value
from openprocurement.api.procedure.types import ListType
from openprocurement.api.validation import validate_items_uniq
from openprocurement.tender.core.procedure.models.bid import MetaBid
from openprocurement.tender.core.procedure.models.bid_document import (
    Document,
    PostDocument,
)
from openprocurement.tender.core.procedure.models.item import LocalizationItem
from openprocurement.tender.core.procedure.models.organization import (
    BusinessOrganization,
)
from openprocurement.tender.core.procedure.models.req_response import (
    ObjResponseMixin,
    PatchObjResponsesMixin,
    PostBidResponsesMixin,
    RequirementResponse,
)
from openprocurement.tender.pricequotation.procedure.validation import (
    validate_bid_value,
)


class PatchBid(PatchObjResponsesMixin, Model):
    value = ModelType(Value)
    tenderers = ListType(ModelType(BusinessOrganization, required=True), min_size=1, max_size=1)
    status = StringType(
        choices=["draft", "pending", "active", "invalid", "invalid.pre-qualification", "unsuccessful", "deleted"],
    )
    items = ListType(ModelType(LocalizationItem, required=True))

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
        ModelType(LocalizationItem, required=True),
        min_size=1,
        validators=[validate_items_uniq],
    )

    def validate_value(self, data, value):
        tender = get_tender()
        validate_bid_value(tender, value)


class Bid(ObjResponseMixin, MetaBid):
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
        ModelType(LocalizationItem, required=True),
        min_size=1,
        validators=[validate_items_uniq],
    )
