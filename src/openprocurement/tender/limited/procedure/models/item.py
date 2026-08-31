from schematics.exceptions import ValidationError
from schematics.types import StringType
from schematics.types.compound import ModelType

from openprocurement.api.procedure.models.address import Address
from openprocurement.api.procedure.models.period import PeriodEndRequired
from openprocurement.tender.core.procedure.models.item import Item as BaseItem
from openprocurement.tender.openua.procedure.models.item import Item as BaseOpenItem


class Item(BaseItem):
    deliveryDate = ModelType(PeriodEndRequired, required=True)
    deliveryAddress = ModelType(Address, required=True)


class ReportingItem(Item):
    product = StringType()
    category = StringType()

    def validate_relatedLot(self, data, value):
        if value:
            raise ValidationError("This option is not available")


class NegotiationItem(BaseOpenItem):
    product = StringType()
