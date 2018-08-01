from schematics.types import MD5Type, StringType
from schematics.types.compound import ModelType
from schematics.transforms import blacklist, whitelist

from openprocurement.api.roles import RolesFromCsv
from openprocurement.api.models import (
    ListType,
    Model,
    Organization,
    IsoDateTimeType,
    schematics_embedded_role,
    schematics_default_role
    )
from openprocurement.agreement.cfaua.models.unitprice\
    import UnitPrice


class Contract(Model):
    class Options:
        roles = {
            'create': blacklist(),
            'edit': whitelist(),
            'embedded': schematics_embedded_role,
            'view': schematics_default_role
        }
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