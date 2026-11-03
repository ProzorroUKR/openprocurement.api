from schematics.types import MD5Type, StringType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.value import Value
from openprocurement.tender.core.procedure.models.value import (
    WeightedValue,
)


class PostLotValue(Model):
    status = StringType(choices=["pending"], default="pending", required=True)
    value = ModelType(Value, required=True)
    relatedLot = MD5Type(required=True)
    subcontractingDetails = StringType()


class PatchLotValue(PostLotValue):
    weightedValue = ModelType(WeightedValue)
    status = StringType(choices=["pending", "active", "unsuccessful"], default="pending")
    date = StringType()


class LotValue(PatchLotValue):
    initialValue = ModelType(Value)  # field added by chronograph
    participationUrl = StringType()  # field added after auction
