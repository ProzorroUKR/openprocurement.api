from schematics.types.compound import ModelType
from openprocurement.api.models import ValidationError
from openprocurement.tender.core.procedure.models.address import Address
from openprocurement.tender.core.procedure.models.period import PeriodEndRequired
from openprocurement.tender.core.procedure.models.item import Item as BaseItem


class Item(BaseItem):
    deliveryDate = ModelType(PeriodEndRequired, required=True)
    deliveryAddress = ModelType(Address, required=True)


class ReportingItem(Item):
    def validate_relatedLot(self, data, value):
        if value:
            raise ValidationError("This option is not available")

