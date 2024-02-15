from schematics.types import StringType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.types import ListType
from openprocurement.api.procedure.validation import validate_parameters_uniq
from openprocurement.tender.cfaselectionua.procedure.models.lot_value import (
    LotValue,
    PatchLotValue,
    PostLotValue,
)
from openprocurement.tender.cfaselectionua.procedure.models.parameter import (
    Parameter,
    PatchParameter,
)
from openprocurement.tender.core.procedure.models.bid import Bid as BaseBid
from openprocurement.tender.core.procedure.models.bid import PatchBid as BasePatchBid
from openprocurement.tender.core.procedure.models.bid import PostBid as BasePostBid
from openprocurement.tender.core.procedure.models.guarantee import WeightedValue
from openprocurement.tender.core.procedure.models.req_response import (
    PatchObjResponsesMixin,
    PostBidResponsesMixin,
)


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
