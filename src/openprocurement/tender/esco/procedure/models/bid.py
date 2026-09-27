from schematics.types import BooleanType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import ListType
from openprocurement.tender.core.procedure.models.bid import Bid, PatchBid, PostBid
from openprocurement.tender.esco.procedure.models.lot_value import ESCOLotValue, ESCOPatchLotValue, ESCOPostLotValue
from openprocurement.tender.esco.procedure.models.value import ESCODynamicValue, ESCOPatchValue, ESCOWeightedValue


class ESCOBidMixin(Model):
    value = ModelType(ESCODynamicValue)
    weightedValue = ModelType(ESCOWeightedValue)
    lotValues = ListType(ModelType(ESCOLotValue, required=True))
    selfQualified = BooleanType(required=False)
    selfEligible = BooleanType(required=False)


class ESCOPatchBid(ESCOBidMixin, PatchBid):
    value = ModelType(ESCOPatchValue)
    lotValues = ListType(ModelType(ESCOPatchLotValue, required=True))


class ESCOPatchQualificationBid(ESCOPatchBid):
    lotValues = ListType(ModelType(ESCOLotValue, required=True))


class ESCOPostBid(ESCOBidMixin, PostBid):
    lotValues = ListType(ModelType(ESCOPostLotValue, required=True))


class ESCOBid(ESCOBidMixin, Bid):
    pass
