from openprocurement.api.models import ListType
from openprocurement.tender.core.models import Bid as BaseBid, validate_parameters_uniq
from openprocurement.tender.cfaselectionua.models.submodels.parameter import Parameter
from schematics.types.compound import ModelType


class Bid(BaseBid):
    parameters = ListType(ModelType(Parameter), default=list(), validators=[validate_parameters_uniq])
