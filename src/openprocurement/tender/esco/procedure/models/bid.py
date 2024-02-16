from schematics.exceptions import ValidationError
from schematics.types import BooleanType
from schematics.types.compound import ModelType

from openprocurement.api.constants import RELEASE_ECRITERIA_ARTICLE_17
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.types import ListType
from openprocurement.tender.core.procedure.utils import tender_created_after
from openprocurement.tender.esco.procedure.models.lot_value import (
    LotValue,
    PatchLotValue,
    PostLotValue,
)
from openprocurement.tender.esco.procedure.models.value import ESCOValue, PatchESCOValue
from openprocurement.tender.openeu.procedure.models.bid import Bid as BaseBid
from openprocurement.tender.openeu.procedure.models.bid import PatchBid as BasePatchBid
from openprocurement.tender.openeu.procedure.models.bid import PostBid as BasePostBid


class ESCOMixin(Model):
    value = ModelType(ESCOValue)
    lotValues = ListType(ModelType(LotValue, required=True))
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

    def validate_selfEligible(self, data, value):
        if tender_created_after(RELEASE_ECRITERIA_ARTICLE_17):
            if value is not None:
                raise ValidationError("Rogue field.")


class PatchBid(ESCOMixin, BasePatchBid):
    value = ModelType(PatchESCOValue)
    lotValues = ListType(ModelType(PatchLotValue, required=True))

    def validate_value(self, data, value):
        return  # will be validated at Bid model


class PostBid(ESCOMixin, BasePostBid):
    lotValues = ListType(ModelType(PostLotValue, required=True))


class Bid(ESCOMixin, BaseBid):
    pass
