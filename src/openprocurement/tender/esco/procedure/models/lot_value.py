from schematics.types.compound import ModelType

from openprocurement.api.procedure.context import get_tender
from openprocurement.tender.core.procedure.models.lot_value import LotValue, PatchLotValue, PostLotValue
from openprocurement.tender.core.procedure.validation import validate_esco_lotvalue_value
from openprocurement.tender.esco.procedure.models.value import ESCODynamicValue, ESCOWeightedValue


class ESCOPostLotValue(PostLotValue):
    value = ModelType(ESCODynamicValue, required=True)

    def validate_value(self, data, value):
        if data.get("status") != "draft":
            if value is not None:
                validate_esco_lotvalue_value(get_tender(), data["relatedLot"], value)


class ESCOPatchLotValue(PatchLotValue):
    value = ModelType(ESCODynamicValue, required=True)
    weightedValue = ModelType(ESCOWeightedValue)

    def validate_value(self, data, value):
        if data.get("status") != "draft":
            if value is not None:
                validate_esco_lotvalue_value(get_tender(), data["relatedLot"], value)


class ESCOLotValue(LotValue):
    value = ModelType(ESCODynamicValue, required=True)
    initialValue = ModelType(ESCODynamicValue)  # field added by chronograph
    weightedValue = ModelType(ESCOWeightedValue)

    def validate_value(self, data, value):
        if data.get("status") != "draft":
            if value is not None:
                validate_esco_lotvalue_value(get_tender(), data["relatedLot"], value)
