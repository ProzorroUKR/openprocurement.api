from schematics.types import BooleanType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.context import get_tender
from openprocurement.api.procedure.types import ListType
from openprocurement.api.procedure.validation import validate_parameters_uniq
from openprocurement.tender.competitiveordering.procedure.models.lot_value import (
    LotValue,
    PostLotValue,
)
from openprocurement.tender.core.procedure.models.bid import LocalizationBid as BaseBid
from openprocurement.tender.core.procedure.models.bid import (
    PatchLocalizationBid as BasePatchBid,
)
from openprocurement.tender.core.procedure.models.bid import (
    PostLocalizationBid as BasePostBid,
)
from openprocurement.tender.core.procedure.models.parameter import (
    Parameter,
    PatchParameter,
)
from openprocurement.tender.core.procedure.models.req_response import (
    PatchObjResponsesMixin,
    PostBidResponsesMixin,
)
from openprocurement.tender.core.procedure.validation import validate_bid_value


class PatchBid(BasePatchBid, PatchObjResponsesMixin):
    selfEligible = BooleanType(choices=[True])
    selfQualified = BooleanType(choices=[True])
    lotValues = ListType(ModelType(LotValue, required=True))
    parameters = ListType(ModelType(PatchParameter, required=True), validators=[validate_parameters_uniq])


class PostBid(BasePostBid, PostBidResponsesMixin):
    selfEligible = BooleanType(choices=[True])
    selfQualified = BooleanType(required=True, choices=[True])
    lotValues = ListType(ModelType(PostLotValue, required=True))
    parameters = ListType(ModelType(Parameter, required=True), validators=[validate_parameters_uniq])

    def validate_value(self, data, value):
        tender = get_tender()
        validate_bid_value(tender, value)


class Bid(BaseBid, PostBidResponsesMixin):
    selfEligible = BooleanType(choices=[True])
    selfQualified = BooleanType(required=True, choices=[True])
    lotValues = ListType(ModelType(LotValue, required=True))
    parameters = ListType(ModelType(Parameter, required=True), validators=[validate_parameters_uniq])

    def validate_value(self, data, value):
        if data.get("status") != "draft":
            tender = get_tender()
            validate_bid_value(tender, value)
