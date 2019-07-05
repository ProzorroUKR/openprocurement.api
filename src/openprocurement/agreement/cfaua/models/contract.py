from schematics.types import MD5Type, StringType
from schematics.types.compound import ModelType

from openprocurement.api.roles import RolesFromCsv
from openprocurement.api.models import (
    ListType,
    Model,
    BusinessOrganization,
    IsoDateTimeType,
)
from openprocurement.agreement.cfaua.models.unitprice\
    import UnitPrice
from openprocurement.agreement.cfaua.models.parameter import Parameter
from openprocurement.agreement.cfaua.validation import validate_parameters_uniq


class Contract(Model):
    class Options:
        roles = RolesFromCsv('Contract.csv', relative_to=__file__)

    id = MD5Type(required=True)

    # TODO: validate me
    status = StringType(
        choices=['active', 'unsuccessful']
    )
    suppliers = ListType(ModelType(BusinessOrganization, required=True))
    unitPrices = ListType(ModelType(UnitPrice, required=True))
    awardID = StringType()
    bidID = StringType()
    date = IsoDateTimeType()
    parameters = ListType(ModelType(Parameter, required=True), default=list(),
                          validators=[validate_parameters_uniq])
