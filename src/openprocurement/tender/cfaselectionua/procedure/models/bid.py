from schematics.types.compound import ModelType

from openprocurement.api.procedure.types import ListType
from openprocurement.api.procedure.validation import validate_parameters_uniq
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
    PostBidResponsesTempMixin,
)


class PatchBid(PatchObjResponsesMixin, BasePatchBid):
    parameters = ListType(ModelType(PatchParameter, required=True), validators=[validate_parameters_uniq])


class PostBid(PostBidResponsesMixin, BasePostBid):
    parameters = ListType(ModelType(Parameter, required=True), validators=[validate_parameters_uniq])


class Bid(PostBidResponsesTempMixin, BaseBid):
    parameters = ListType(ModelType(Parameter, required=True), validators=[validate_parameters_uniq])
    weightedValue = ModelType(WeightedValue)
