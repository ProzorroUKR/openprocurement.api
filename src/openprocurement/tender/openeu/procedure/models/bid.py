from schematics.types import BooleanType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.types import ListType
from openprocurement.tender.core.procedure.models.document import Document, PostDocument
from openprocurement.tender.core.procedure.models.guarantee import WeightedValue
from openprocurement.tender.core.procedure.models.lot_value import (
    LotValue,
    PatchLotValue,
    PostLotValue,
)
from openprocurement.tender.openua.procedure.models.bid import Bid as BaseBid
from openprocurement.tender.openua.procedure.models.bid import PatchBid as BasePatchBid
from openprocurement.tender.openua.procedure.models.bid import PostBid as BasePostBid


class PatchBid(BasePatchBid):
    lotValues = ListType(ModelType(PatchLotValue, required=True))
    selfQualified = BooleanType(choices=[True])  # selfQualified, selfEligible are the same as in the parent but
    selfEligible = BooleanType(choices=[True])  # tests fail because they in different order


class PostBid(BasePostBid):
    lotValues = ListType(ModelType(PostLotValue, required=True))

    documents = ListType(ModelType(PostDocument, required=True))
    financialDocuments = ListType(ModelType(PostDocument, required=True))
    eligibilityDocuments = ListType(ModelType(PostDocument, required=True))
    qualificationDocuments = ListType(ModelType(PostDocument, required=True))

    selfQualified = BooleanType(required=True, choices=[True])
    selfEligible = BooleanType(choices=[True])


class Bid(BaseBid):
    lotValues = ListType(ModelType(LotValue, required=True))

    weightedValue = ModelType(WeightedValue)

    documents = ListType(ModelType(Document, required=True))
    financialDocuments = ListType(ModelType(Document, required=True))
    eligibilityDocuments = ListType(ModelType(Document, required=True))
    qualificationDocuments = ListType(ModelType(Document, required=True))

    selfQualified = BooleanType(required=True, choices=[True])
