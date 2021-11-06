from schematics.types.compound import ModelType
from schematics.types import StringType
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.esco.procedure.models.value import ESCOValue, PatchESCOValue
from openprocurement.tender.openua.procedure.models.lot_value import (
    PostLotValue as BasePostLotValue,
    PatchLotValue as BasePatchLotValue,
)
from schematics.exceptions import ValidationError


class PostLotValue(BasePostLotValue):
    status = StringType(choices=["pending", "active"], default="pending")
    value = ModelType(ESCOValue, required=True)

    def validate_value(self, data, value):
        if data.get("status") != "draft":
            tender = get_tender()
            if value and tender["status"] not in ("invalid", "deleted", "draft") and data["relatedLot"]:
                lots = [lot for lot in tender.get("lots", "") if lot and lot["id"] == data["relatedLot"]]
                if not lots:
                    return
                lot = lots[0]
                if lot["minValue"].get("currency") != value.get("currency"):
                    raise ValidationError("currency of bid should be identical to currency of minValue of lot")
                if lot["minValue"].get("valueAddedTaxIncluded") != value.get("valueAddedTaxIncluded"):
                    raise ValidationError(
                        "valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of minValue of lot"
                    )


class PatchLotValue(BasePatchLotValue):
    status = StringType(choices=["pending", "active"], default="pending")
    value = ModelType(PatchESCOValue)

    def validate_value(self, data, value):
        return  # depends on status,  will be validated in LotValue model


class LotValue(PostLotValue):
    date = StringType()
    status = StringType(choices=["pending", "active", "unsuccessful"])
