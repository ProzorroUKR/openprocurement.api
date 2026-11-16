from openprocurement.tender.arma.procedure.models.lot_value import ARMALotValue, ARMAPatchLotValue, ARMAPostLotValue
from openprocurement.tender.core.procedure.models.bid import Bid, PatchBid, PostBid
from openprocurement.tender.core.procedure.models.value import AmountPercentageWeightedValue


class ARMAPatchBid(PatchBid):
    lotValues: list[ARMAPatchLotValue] | None = None


class ARMAPatchQualificationBid(ARMAPatchBid):
    lotValues: list[ARMALotValue] | None = None


class ARMAPostBid(PostBid):
    lotValues: list[ARMAPostLotValue] | None = None


class ARMABid(Bid):
    lotValues: list[ARMALotValue] | None = None
    weightedValue: AmountPercentageWeightedValue | None = None
