from openprocurement.tender.core.procedure.models.lot_value import LotValue, PatchLotValue, PostLotValue
from openprocurement.tender.esco.procedure.models.value import ESCODynamicValue, ESCOWeightedValue


class ESCOPostLotValue(PostLotValue):
    value: ESCODynamicValue


class ESCOPatchLotValue(PatchLotValue):
    value: ESCODynamicValue
    weightedValue: ESCOWeightedValue | None = None


class ESCOLotValue(LotValue):
    value: ESCODynamicValue
    initialValue: ESCODynamicValue | None = None
    weightedValue: ESCOWeightedValue | None = None
