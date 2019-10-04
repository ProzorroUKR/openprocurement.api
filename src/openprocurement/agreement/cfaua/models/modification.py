from decimal import Decimal
from schematics.types import StringType
from openprocurement.api.models import DecimalType, Model
from openprocurement.api.roles import RolesFromCsv


class UnitPriceModification(Model):
    class Options:
        roles = RolesFromCsv("UnitPriceModification.csv", relative_to=__file__)

    itemId = StringType()
    factor = DecimalType(required=False, precision=-4, min_value=Decimal("0.0"))
    addend = DecimalType(required=False, precision=-2)


class ContractModification(Model):
    class Options:
        roles = RolesFromCsv("ContractModification.csv", relative_to=__file__)

    itemId = StringType()
    contractId = StringType(required=True)
