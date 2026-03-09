from schematics.exceptions import ValidationError
from schematics.types import MD5Type, StringType

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.value import AmountPercentageValue
from openprocurement.api.procedure.types import ModelType
from openprocurement.tender.core.procedure.models.value import (
    AmountPercentageWeightedValue,
)
from openprocurement.tender.core.procedure.utils import find_lot
from openprocurement.tender.core.procedure.validation import validate_related_lot


class PostLotValue(Model):
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


class PatchLotValue(PostLotValue):
    weightedValue = ModelType(AmountPercentageWeightedValue)
    status = StringType(choices=["pending", "active", "unsuccessful"], default="pending")
    date = StringType()


class LotValue(PatchLotValue):
    initialValue = ModelType(AmountPercentageValue)  # field added by chronograph
    participationUrl = StringType()  # field added after auction
