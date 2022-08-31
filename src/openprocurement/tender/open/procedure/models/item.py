from openprocurement.tender.core.procedure.models.item import Item as BaseItem
from openprocurement.tender.core.procedure.models.period import PeriodEndRequired
from openprocurement.tender.core.procedure.models.base import ModelType
from openprocurement.tender.core.procedure.models.address import Address


class Item(BaseItem):
    deliveryDate = ModelType(PeriodEndRequired, required=True)
    deliveryAddress = ModelType(Address, required=True)
