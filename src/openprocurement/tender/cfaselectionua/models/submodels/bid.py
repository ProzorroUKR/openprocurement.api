from openprocurement.api.models import ListType
from openprocurement.api.roles import RolesFromCsv
from openprocurement.tender.core.models import Bid as BaseBid, BidResponsesMixin, validate_parameters_uniq
from openprocurement.tender.cfaselectionua.models.submodels.parameter import Parameter
from schematics.types.compound import ModelType
from schematics.types import StringType
from openprocurement.tender.core.models import LotValue as BaseLotValue


class LotValue(BaseLotValue):
    class Options:
        roles = RolesFromCsv("LotValue.csv", relative_to=__file__)

    subcontractingDetails = StringType()


class Bid(BaseBid, BidResponsesMixin):
    class Options:
        roles = RolesFromCsv("Bid.csv", relative_to=__file__)

    parameters = ListType(ModelType(Parameter, required=True), default=list(), validators=[validate_parameters_uniq])
    subcontractingDetails = StringType()
    lotValues = ListType(ModelType(LotValue, required=True), default=list())
