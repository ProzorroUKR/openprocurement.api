from schematics.types import MD5Type, StringType
from schematics.types.compound import ModelType

from openprocurement.api.roles import RolesFromCsv
from openprocurement.api.models import (
    ListType,
    Model,
    Organization,
    IsoDateTimeType,
    )
from openprocurement.agreement.cfaua.models.unitprice\
    import UnitPrice


class Contract(Model):
    class Options:
        roles = RolesFromCsv('Contract.csv', relative_to=__file__)

    id = MD5Type(required=True)

    # TODO: validate me
    status = StringType(
        choices=['active', 'unsuccessful']
    )
    suppliers = ListType(ModelType(Organization))
    unitPrices = ListType(ModelType(UnitPrice))
    awardID = StringType()
    bidID = StringType()
    date = IsoDateTimeType()
