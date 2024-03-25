from openprocurement.tender.core.procedure.models.item import BaseItem
from openprocurement.tender.core.procedure.models.item import Item as TenderBaseItem


class BidItem(BaseItem):
    def validate_quantity(self, data, value):
        pass


class Item(TenderBaseItem):
    def validate_unit(self, data, value):
        pass

    def validate_quantity(self, data, value):
        pass
