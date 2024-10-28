from uuid import uuid4

from schematics.types import BooleanType, StringType
from schematics.types.compound import ModelType
from schematics.types.serializable import serializable

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.types import ListType
from openprocurement.api.validation import validate_items_uniq
from openprocurement.tender.competitivedialogue.procedure.models.bid_document import (
    Document,
    PostDocument,
)
from openprocurement.tender.competitivedialogue.procedure.models.item import BidItem
from openprocurement.tender.competitivedialogue.procedure.models.lot_value import (
    LotValue,
    PostLotValue,
)
from openprocurement.tender.core.procedure.models.base import BaseBid
from openprocurement.tender.core.procedure.models.bid import (
    MetaBid,
    validate_lot_values,
)
from openprocurement.tender.core.procedure.models.organization import (
    BusinessOrganization,
)
from openprocurement.tender.core.procedure.models.req_response import (
    PatchObjResponsesMixin,
    PostBidResponsesMixin,
    PostBidResponsesTempMixin,
)
from openprocurement.tender.core.procedure.validation import validate_bid_value


class PatchBid(PatchObjResponsesMixin, BaseBid):
    items = ListType(ModelType(BidItem, required=True))
    tenderers = ListType(ModelType(BusinessOrganization, required=True), min_size=1, max_size=1)
    lotValues = ListType(ModelType(LotValue, required=True))
    subcontractingDetails = StringType()
    selfQualified = BooleanType(choices=[True])
    selfEligible = BooleanType(choices=[True])
    status = StringType(
        choices=[
            "draft",
            "pending",
            "active",
            "invalid",
            "invalid.pre-qualification",
            "unsuccessful",
            "deleted",
        ],
    )


class PostBid(PostBidResponsesMixin, BaseBid):
    @serializable
    def id(self):
        return uuid4().hex

    items = ListType(ModelType(BidItem, required=True), min_size=1, validators=[validate_items_uniq])
    tenderers = ListType(
        ModelType(BusinessOrganization, required=True),
        required=True,
        min_size=1,
        max_size=1,
    )
    subcontractingDetails = StringType()
    lotValues = ListType(ModelType(PostLotValue, required=True))
    documents = ListType(ModelType(PostDocument, required=True))
    financialDocuments = ListType(ModelType(PostDocument, required=True))
    eligibilityDocuments = ListType(ModelType(PostDocument, required=True))
    qualificationDocuments = ListType(ModelType(PostDocument, required=True))

    selfQualified = BooleanType(required=True, choices=[True])
    selfEligible = BooleanType(choices=[True])
    status = StringType(
        choices=[
            "draft",
            "pending",
            "active",
            "invalid",
            "invalid.pre-qualification",
            "unsuccessful",
            "deleted",
        ],
        default="draft",
    )

    def validate_value(self, data, value):
        tender = get_tender()
        validate_bid_value(tender, value)

    def validate_lotValues(self, data, values):
        validate_lot_values(values)


class Bid(MetaBid, PostBidResponsesTempMixin, BaseBid):
    items = ListType(ModelType(BidItem, required=True), min_size=1, validators=[validate_items_uniq])
    tenderers = ListType(
        ModelType(BusinessOrganization, required=True),
        required=True,
        min_size=1,
        max_size=1,
    )
    lotValues = ListType(ModelType(LotValue, required=True))
    documents = ListType(ModelType(Document, required=True))
    financialDocuments = ListType(ModelType(Document, required=True))
    eligibilityDocuments = ListType(ModelType(Document, required=True))
    qualificationDocuments = ListType(ModelType(Document, required=True))
    subcontractingDetails = StringType()
    selfQualified = BooleanType(required=True, choices=[True])
    selfEligible = BooleanType(choices=[True])
    status = StringType(
        choices=[
            "draft",
            "pending",
            "active",
            "invalid",
            "invalid.pre-qualification",
            "unsuccessful",
            "deleted",
        ],
    )

    def validate_value(self, data, value):
        tender = get_tender()
        validate_bid_value(tender, value)

    def validate_lotValues(self, data, values):
        validate_lot_values(values)
