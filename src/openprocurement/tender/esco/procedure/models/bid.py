from openprocurement.api.procedure.models.base import Model
from openprocurement.tender.core.procedure.models.bid import Bid, PatchBid, PostBid
from openprocurement.tender.esco.procedure.models.lot_value import ESCOLotValue, ESCOPatchLotValue, ESCOPostLotValue
from openprocurement.tender.esco.procedure.models.value import ESCODynamicValue, ESCOPatchValue, ESCOWeightedValue


class ESCOBidMixin(Model):
    value: ESCODynamicValue | None = None
    weightedValue: ESCOWeightedValue | None = None
    lotValues: list[ESCOLotValue] | None = None
    selfQualified: bool | None = None
    selfEligible: bool | None = None


class ESCOPatchBid(ESCOBidMixin, PatchBid):
    value: ESCOPatchValue | None = None
    lotValues: list[ESCOPatchLotValue] | None = None


class ESCOPatchQualificationBid(ESCOPatchBid):
    lotValues: list[ESCOLotValue] | None = None


class ESCOPostBid(ESCOBidMixin, PostBid):
    lotValues: list[ESCOPostLotValue] | None = None


class ESCOBid(ESCOBidMixin, Bid):
    pass
