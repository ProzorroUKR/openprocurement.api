from schematics.exceptions import ValidationError
from schematics.types import BooleanType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import ListType
from openprocurement.tender.core.procedure.models.bid import Bid, PatchBid, PostBid
from openprocurement.tender.esco.procedure.models.lot_value import ESCOLotValue, ESCOPatchLotValue, ESCOPostLotValue
from openprocurement.tender.esco.procedure.models.value import ESCODynamicValue, ESCOPatchValue, ESCOWeightedValue


class ESCOBidMixin(Model):
    value = ModelType(ESCODynamicValue)
    weightedValue = ModelType(ESCOWeightedValue)
    lotValues = ListType(ModelType(ESCOLotValue, required=True))
    selfQualified = BooleanType(required=False)
    selfEligible = BooleanType(required=False)

    def validate_value(self, data, value):
        tender = get_tender()
        if tender.get("lots"):
            if value:
                raise ValidationError("value should be posted for each lot of bid")
        else:
            if not value:
                raise ValidationError("This field is required.")
            if tender["minValue"].get("currency") != value.get("currency"):
                raise ValidationError("currency of bid should be identical to currency of minValue of tender")
            if tender["minValue"].get("valueAddedTaxIncluded") != value.get("valueAddedTaxIncluded"):
                raise ValidationError(
                    "valueAddedTaxIncluded of bid should be identical to valueAddedTaxIncluded of minValue of tender"
                )


class ESCOPatchBid(ESCOBidMixin, PatchBid):
    value = ModelType(ESCOPatchValue)
    lotValues = ListType(ModelType(ESCOPatchLotValue, required=True))

    def validate_value(self, data, value):
        return  # will be validated at Bid model


class ESCOPatchQualificationBid(ESCOPatchBid):
    lotValues = ListType(ModelType(ESCOLotValue, required=True))


class ESCOPostBid(ESCOBidMixin, PostBid):
    lotValues = ListType(ModelType(ESCOPostLotValue, required=True))


class ESCOBid(ESCOBidMixin, Bid):
    pass
