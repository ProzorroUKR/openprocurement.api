from schematics.types import BooleanType, StringType
from schematics.types.compound import ModelType
from openprocurement.tender.openua.procedure.models.lot_value import LotValue, PostLotValue, PatchLotValue
from openprocurement.tender.core.procedure.models.bid import (
    PostBid as BasePostBid,
    PatchBid as BasePatchBid,
    Bid as BaseBid,
)
from openprocurement.tender.core.procedure.models.parameter import Parameter, PatchParameter
from openprocurement.api.procedure.types import ListType
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.core.procedure.validation import validate_bid_value
from openprocurement.api.procedure.validation import validate_parameters_uniq


class PostBid(BasePostBid):
    selfEligible = BooleanType(choices=[True], required=True)
    selfQualified = BooleanType(choices=[True], required=True)
    subcontractingDetails = StringType()
    lotValues = ListType(ModelType(PostLotValue, required=True))
    parameters = ListType(ModelType(Parameter, required=True), validators=[validate_parameters_uniq])

    def validate_value(self, data, value):
        tender = get_tender()
        validate_bid_value(tender, value)


class PatchBid(BasePatchBid):
    selfEligible = BooleanType(choices=[True])
    selfQualified = BooleanType(choices=[True])
    subcontractingDetails = StringType()
    lotValues = ListType(ModelType(PatchLotValue, required=True))
    parameters = ListType(ModelType(PatchParameter, required=True), validators=[validate_parameters_uniq])


class Bid(BaseBid):
    selfEligible = BooleanType(choices=[True], required=True)
    selfQualified = BooleanType(choices=[True], required=True)
    subcontractingDetails = StringType()
    lotValues = ListType(ModelType(LotValue, required=True))
    parameters = ListType(ModelType(Parameter, required=True), validators=[validate_parameters_uniq])

    def validate_value(self, data, value):
        tender = get_tender()
        validate_bid_value(tender, value)

