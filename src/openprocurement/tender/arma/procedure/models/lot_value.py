from schematics.types import MD5Type, StringType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.value import AmountPercentageValue
from openprocurement.tender.core.procedure.models.value import AmountPercentageWeightedValue


class ARMAPostLotValue(Model):
    status = StringType(choices=["pending"], default="pending", required=True)
    value = ModelType(AmountPercentageValue, required=True)
    relatedLot = MD5Type(required=True)
    subcontractingDetails = StringType()


class ARMAPatchLotValue(ARMAPostLotValue):
    weightedValue = ModelType(AmountPercentageWeightedValue)
    status = StringType(choices=["pending", "active", "unsuccessful"], default="pending")
    date = StringType()


class ARMALotValue(ARMAPatchLotValue):
    initialValue = ModelType(AmountPercentageValue)  # field added by chronograph
    participationUrl = StringType()  # field added after auction
