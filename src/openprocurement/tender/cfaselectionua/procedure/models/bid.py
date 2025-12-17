from schematics.types.compound import ModelType

from openprocurement.api.procedure.types import ListType
from openprocurement.api.validation import validate_uniq_code
from openprocurement.tender.cfaselectionua.procedure.models.parameter import (
    Parameter,
    PatchParameter,
)
from openprocurement.tender.core.procedure.models.bid import Bid as BaseBid
from openprocurement.tender.core.procedure.models.bid import PatchBid as BasePatchBid
from openprocurement.tender.core.procedure.models.bid import (
    PatchQualificationBid as BasePatchQualificationBid,
)
from openprocurement.tender.core.procedure.models.bid import PostBid as BasePostBid
from openprocurement.tender.core.procedure.models.req_response import (
    BidResponsesMixin,
    PatchObjResponsesMixin,
)
from openprocurement.tender.core.procedure.models.value import WeightedValue


class PatchBid(PatchObjResponsesMixin, BasePatchBid):
    parameters = ListType(ModelType(PatchParameter, required=True), validators=[validate_uniq_code])


class PatchQualificationBid(PatchObjResponsesMixin, BasePatchQualificationBid):
    parameters = ListType(ModelType(PatchParameter, required=True), validators=[validate_uniq_code])


class PostBid(BidResponsesMixin, BasePostBid):
    parameters = ListType(ModelType(Parameter, required=True), validators=[validate_uniq_code])


class Bid(BidResponsesMixin, BaseBid):
    parameters = ListType(ModelType(Parameter, required=True), validators=[validate_uniq_code])
    weightedValue = ModelType(WeightedValue)
