from schematics.types.compound import ModelType

from openprocurement.api.procedure.types import ListType
from openprocurement.api.validation import validate_uniq_code
from openprocurement.tender.cfaselectionua.procedure.models.parameter import (
    Parameter,
    PatchParameter,
)
from openprocurement.tender.core.procedure.models.bid import (
    LocalizationBid as BaseLocalizationBid,
)
from openprocurement.tender.core.procedure.models.bid import (
    PatchLocalizationBid as BasePatchLocalizationBid,
)
from openprocurement.tender.core.procedure.models.bid import (
    PatchQualificationLocalizationBid as BasePatchQualificationLocalizationBid,
)
from openprocurement.tender.core.procedure.models.bid import (
    PostLocalizationBid as BasePostLocalizationBid,
)
from openprocurement.tender.core.procedure.models.req_response import (
    BidResponsesMixin,
    PatchObjResponsesMixin,
)
from openprocurement.tender.core.procedure.models.value import WeightedValue


class PatchBid(PatchObjResponsesMixin, BasePatchLocalizationBid):
    parameters = ListType(ModelType(PatchParameter, required=True), validators=[validate_uniq_code])


class PatchQualificationBid(PatchObjResponsesMixin, BasePatchQualificationLocalizationBid):
    parameters = ListType(ModelType(PatchParameter, required=True), validators=[validate_uniq_code])


class PostBid(BidResponsesMixin, BasePostLocalizationBid):
    parameters = ListType(ModelType(Parameter, required=True), validators=[validate_uniq_code])


class Bid(BidResponsesMixin, BaseLocalizationBid):
    parameters = ListType(ModelType(Parameter, required=True), validators=[validate_uniq_code])
    weightedValue = ModelType(WeightedValue)
