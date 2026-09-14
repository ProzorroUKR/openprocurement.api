from schematics.types.compound import ModelType

from openprocurement.api.procedure.types import ListType
from openprocurement.tender.arma.procedure.models.lot_value import ARMALotValue, ARMAPatchLotValue, ARMAPostLotValue
from openprocurement.tender.core.procedure.models.bid import Bid, PatchBid, PostBid
from openprocurement.tender.core.procedure.models.value import AmountPercentageWeightedValue


class ARMAPatchBid(PatchBid):
    lotValues = ListType(ModelType(ARMAPatchLotValue, required=True))


class ARMAPatchQualificationBid(ARMAPatchBid):
    lotValues = ListType(ModelType(ARMALotValue, required=True))


class ARMAPostBid(PostBid):
    lotValues = ListType(ModelType(ARMAPostLotValue, required=True))


class ARMABid(Bid):
    lotValues = ListType(ModelType(ARMALotValue, required=True))
    weightedValue = ModelType(AmountPercentageWeightedValue)
