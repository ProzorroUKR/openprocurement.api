from decimal import Decimal
from schematics.types import StringType
from openprocurement.api.models import DecimalType, Model
from openprocurement.api.roles import RolesFromCsv


class UnitPriceModifiaction(Model):
    class Options:
        roles = RolesFromCsv('UnitPriceModifiaction.csv', relative_to=__file__)

    itemId = StringType()
    factor = DecimalType(required=False, precision=-4, min_value=Decimal('0.0'))
    addend = DecimalType(required=False, precision=-2)


class ContractModifiaction(Model):
    class Options:
        roles = RolesFromCsv('ContractModifiaction.csv', relative_to=__file__)

    itemId = StringType()
    contractId = StringType(required=True)
