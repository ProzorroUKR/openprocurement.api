from schematics.types import BooleanType
from schematics.types.compound import ModelType

from openprocurement.tender.core.procedure.models.bid import LocalizationBid as BaseBid
from openprocurement.tender.core.procedure.models.bid import (
    PatchLocalizationBid as BasePatchBid,
)
from openprocurement.tender.core.procedure.models.bid import (
    PostLocalizationBid as BasePostBid,
)
from openprocurement.tender.core.procedure.models.guarantee import WeightedValue
from openprocurement.tender.core.procedure.models.req_response import (
    BidResponsesMixin,
    PatchObjResponsesMixin,
)


class PatchBid(PatchObjResponsesMixin, BasePatchBid):
    selfQualified = BooleanType(choices=[True])  # selfQualified, selfEligible are the same as in the parent but
    selfEligible = BooleanType(choices=[True])  # tests fail because they in different order


class PostBid(BidResponsesMixin, BasePostBid):
    selfQualified = BooleanType(required=True, choices=[True])
    selfEligible = BooleanType(choices=[True])


class Bid(BidResponsesMixin, BaseBid):
    weightedValue = ModelType(WeightedValue)
    selfQualified = BooleanType(required=True, choices=[True])
