from schematics.types import StringType

from openprocurement.api.procedure.models.period import PeriodEndRequired
from openprocurement.api.procedure.types import ModelType
from openprocurement.tender.core.procedure.models.address import Address
from openprocurement.tender.core.procedure.models.item import Item as BaseItem


class Item(BaseItem):
    deliveryDate = ModelType(PeriodEndRequired, required=True)
    deliveryAddress = ModelType(Address, required=True)

    description_en = StringType(required=True, min_length=1)
