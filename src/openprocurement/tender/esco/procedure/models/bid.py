from schematics.types import BooleanType
from openprocurement.api.context import get_now
from openprocurement.api.models import Model
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.core.procedure.utils import get_first_revision_date
from openprocurement.tender.openeu.procedure.models.bid import (
    Bid as BaseBid,
    PostBid as BasePostBid,
    PatchBid as BasePatchBid,
)
from openprocurement.tender.esco.procedure.models.lot_value import LotValue, PatchLotValue, PostLotValue
from openprocurement.tender.esco.procedure.models.value import ESCOValue, PatchESCOValue
from openprocurement.tender.core.procedure.models.base import ListType
from openprocurement.api.constants import RELEASE_ECRITERIA_ARTICLE_17
from schematics.types.compound import ModelType
from schematics.exceptions import ValidationError


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
        tender = get_tender()
        if get_first_revision_date(tender, default=get_now()) > RELEASE_ECRITERIA_ARTICLE_17:
            if value is not None:
                raise ValidationError("Rogue field.")


class PatchBid(ESCOMixin, BasePatchBid):
    value = ModelType(PatchESCOValue)
    lotValues = ListType(ModelType(PatchLotValue, required=True))

    def validate_value(self, data, value):
        return   # will be validated at Bid model


class PostBid(ESCOMixin, BasePostBid):
    lotValues = ListType(ModelType(PostLotValue, required=True))


class Bid(ESCOMixin, BaseBid):
    pass
