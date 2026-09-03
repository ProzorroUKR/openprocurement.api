from schematics.exceptions import ValidationError
from schematics.types import MD5Type, StringType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.value import AmountPercentageValue, Value
from openprocurement.tender.core.procedure.models.value import (
    AmountPercentageWeightedValue,
    ESCODynamicValue,
    ESCOWeightedValue,
    WeightedValue,
)
from openprocurement.tender.core.procedure.utils import find_lot
from openprocurement.tender.core.procedure.validation import (
    validate_esco_lotvalue_value,
    validate_lotvalue_value,
    validate_related_lot,
)


class PostLotValue(Model):
    status = StringType(choices=["pending"], default="pending", required=True)
    value = ModelType(Value, required=True)
    relatedLot = MD5Type(required=True)
    subcontractingDetails = StringType()

    def validate_value(self, data, value):
        validate_lotvalue_value(get_tender(), data["relatedLot"], value)

    def validate_relatedLot(self, data, related_lot):
        validate_related_lot(get_tender(), related_lot)


class PatchLotValue(PostLotValue):
    weightedValue = ModelType(WeightedValue)
    status = StringType(choices=["pending", "active", "unsuccessful"], default="pending")
    date = StringType()


class LotValue(PatchLotValue):
    initialValue = ModelType(Value)  # field added by chronograph
    participationUrl = StringType()  # field added after auction


# --- ESCO ---


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


# --- ARMA (percentage values) ---


class ARMAPostLotValue(Model):
    status = StringType(choices=["pending"], default="pending", required=True)
    value = ModelType(AmountPercentageValue, required=True)
    relatedLot = MD5Type(required=True)
    subcontractingDetails = StringType()

    def validate_value(self, data, value):
        lot = find_lot(get_tender(), data["relatedLot"])
        if lot and value:
            tender_lot_value = lot.get("value")
            if tender_lot_value["amountPercentage"] < value["amountPercentage"]:
                raise ValidationError("value of bid should be less than value of lot")

    def validate_relatedLot(self, data, related_lot):
        validate_related_lot(get_tender(), related_lot)


class ARMAPatchLotValue(ARMAPostLotValue):
    weightedValue = ModelType(AmountPercentageWeightedValue)
    status = StringType(choices=["pending", "active", "unsuccessful"], default="pending")
    date = StringType()


class ARMALotValue(ARMAPatchLotValue):
    initialValue = ModelType(AmountPercentageValue)  # field added by chronograph
    participationUrl = StringType()  # field added after auction


# --- competitiveDialogue (stage 1): lot values without a value ---


class CDPatchLotValue(Model):
    relatedLot = MD5Type()
    subcontractingDetails = StringType()
    status = StringType(choices=["pending", "active", "unsuccessful"], default="pending")
    date = StringType()

    def validate_relatedLot(self, data, related_lot):
        tender = get_tender()
        validate_related_lot(tender, related_lot)


class CDLotValue(CDPatchLotValue):
    initialValue = ModelType(Value)  # field added by chronograph
    participationUrl = StringType()  # field added after auction


class CDPostLotValue(Model):
    relatedLot = MD5Type()
    subcontractingDetails = StringType()
    status = StringType(choices=["pending"], default="pending")

    def validate_relatedLot(self, data, related_lot):
        tender = get_tender()
        validate_related_lot(tender, related_lot)
