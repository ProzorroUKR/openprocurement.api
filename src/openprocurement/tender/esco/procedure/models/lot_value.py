from schematics.types.compound import ModelType

from openprocurement.tender.core.procedure.models.lot_value import LotValue, PatchLotValue, PostLotValue
from openprocurement.tender.esco.procedure.models.value import ESCODynamicValue, ESCOWeightedValue


class ESCOPostLotValue(PostLotValue):
    value = ModelType(ESCODynamicValue, required=True)


class ESCOPatchLotValue(PatchLotValue):
    value = ModelType(ESCODynamicValue, required=True)
    weightedValue = ModelType(ESCOWeightedValue)


class ESCOLotValue(LotValue):
    value = ModelType(ESCODynamicValue, required=True)
    initialValue = ModelType(ESCODynamicValue)  # field added by chronograph
    weightedValue = ModelType(ESCOWeightedValue)
