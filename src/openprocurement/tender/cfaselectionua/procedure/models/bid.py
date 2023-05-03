from schematics.types import StringType

from openprocurement.tender.core.procedure.models.guarantee import WeightedValue
from openprocurement.tender.core.procedure.models.req_response import PostBidResponsesMixin, PatchObjResponsesMixin
from openprocurement.tender.core.procedure.models.bid import (
    Bid as BaseBid,
    PostBid as BasePostBid,
    PatchBid as BasePatchBid,
)
from openprocurement.tender.cfaselectionua.procedure.models.lot_value import LotValue, PostLotValue, PatchLotValue
from openprocurement.tender.cfaselectionua.procedure.models.parameter import PatchParameter, Parameter
from openprocurement.tender.core.procedure.models.base import ListType
from schematics.types.compound import ModelType
from openprocurement.tender.core.models import validate_parameters_uniq


class PatchBid(PatchObjResponsesMixin, BasePatchBid):
    parameters = ListType(ModelType(PatchParameter, required=True), validators=[validate_parameters_uniq])
    lotValues = ListType(ModelType(PatchLotValue, required=True))
    subcontractingDetails = StringType()


class PostBid(PostBidResponsesMixin, BasePostBid):
    parameters = ListType(ModelType(Parameter, required=True), validators=[validate_parameters_uniq])
    lotValues = ListType(ModelType(PostLotValue, required=True))
    subcontractingDetails = StringType()


class Bid(PostBidResponsesMixin, BaseBid):
    parameters = ListType(ModelType(Parameter, required=True), validators=[validate_parameters_uniq])
    lotValues = ListType(ModelType(LotValue, required=True))
    subcontractingDetails = StringType()
    weightedValue = ModelType(WeightedValue)
