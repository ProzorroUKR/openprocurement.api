from schematics.types import StringType, BooleanType

from openprocurement.tender.core.procedure.models.guarantee import WeightedValue
from openprocurement.tender.core.procedure.models.req_response import PostBidResponsesMixin, PatchObjResponsesMixin
from openprocurement.tender.core.procedure.models.bid import (
    Bid as BaseBid,
    PostBid as BasePostBid,
    PatchBid as BasePatchBid,
    get_default_bid_status,
)
from openprocurement.tender.core.procedure.models.base import ListType
from openprocurement.tender.cfaua.procedure.models.lot_value import LotValue, PostLotValue, PatchLotValue
from openprocurement.tender.openeu.procedure.models.document import (
    PostDocument,
    Document,
)
from schematics.types.compound import ModelType


class PatchBid(PatchObjResponsesMixin, BasePatchBid):
    subcontractingDetails = StringType()
    lotValues = ListType(ModelType(PatchLotValue, required=True))
    selfQualified = BooleanType(choices=[True])  # selfQualified, selfEligible are the same as in the parent but
    selfEligible = BooleanType(choices=[True])   # tests fail because they in different order
    status = StringType(
        choices=["draft", "pending", "active", "invalid", "invalid.pre-qualification", "unsuccessful", "deleted"],
    )


class PostBid(PostBidResponsesMixin, BasePostBid):
    subcontractingDetails = StringType()
    lotValues = ListType(ModelType(PostLotValue, required=True))

    documents = ListType(ModelType(PostDocument, required=True))
    financialDocuments = ListType(ModelType(PostDocument, required=True))
    eligibilityDocuments = ListType(ModelType(PostDocument, required=True))
    qualificationDocuments = ListType(ModelType(PostDocument, required=True))

    selfQualified = BooleanType(required=True, choices=[True])
    selfEligible = BooleanType(choices=[True])
    status = StringType(
        choices=["draft", "pending", "active", "invalid", "invalid.pre-qualification", "unsuccessful", "deleted"],
        default=get_default_bid_status("pending")
    )


class Bid(PostBidResponsesMixin, BaseBid):
    subcontractingDetails = StringType()
    lotValues = ListType(ModelType(LotValue, required=True))

    weightedValue = ModelType(WeightedValue)

    documents = ListType(ModelType(Document, required=True))
    financialDocuments = ListType(ModelType(Document, required=True))
    eligibilityDocuments = ListType(ModelType(Document, required=True))
    qualificationDocuments = ListType(ModelType(Document, required=True))

    selfQualified = BooleanType(required=True, choices=[True])

    status = StringType(
        choices=["draft", "pending", "active", "invalid", "invalid.pre-qualification", "unsuccessful", "deleted"],
        required=True
    )
