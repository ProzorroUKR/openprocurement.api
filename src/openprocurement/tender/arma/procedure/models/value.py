from decimal import Decimal

from schematics.exceptions import ValidationError
from schematics.types import FloatType, MD5Type, StringType

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import (
    DecimalType,
    ModelType,
    NormalizedDecimalType,
)
from openprocurement.tender.core.procedure.utils import find_lot
from openprocurement.tender.core.procedure.validation import validate_related_lot

MIN_VALUE = Decimal("0")
MAX_VALUE = Decimal("100")
PRECISION = -3


class Value(Model):
    amountPercentage = NormalizedDecimalType(
        min_value=MIN_VALUE,
        max_value=MAX_VALUE,
        precision=PRECISION,
        required=True,
    )


class WeightedValue(Model):
    amountPercentage = NormalizedDecimalType(required=True)
    denominator = FloatType()
    addition = DecimalType(precision=-2)


class PostLotValue(Model):
    status = StringType(choices=["pending"], default="pending", required=True)
    value = ModelType(Value, required=True)
    relatedLot = MD5Type(required=True)
    subcontractingDetails = StringType()

    def validate_value(self, data, value):
        lot = find_lot(get_tender(), data["relatedLot"])
        if lot and value:
            tender_lot_value = lot.get("value")
            if float(tender_lot_value["amountPercentage"]) < value["amountPercentage"]:
                raise ValidationError("value of bid should be less than value of lot")

    def validate_relatedLot(self, data, related_lot):
        validate_related_lot(get_tender(), related_lot)


class PatchLotValue(PostLotValue):
    weightedValue = ModelType(WeightedValue)
    status = StringType(choices=["pending", "active", "unsuccessful"], default="pending")
    date = StringType()


class LotValue(PatchLotValue):
    initialValue = ModelType(Value)  # field added by chronograph
    participationUrl = StringType()  # field added after auction
