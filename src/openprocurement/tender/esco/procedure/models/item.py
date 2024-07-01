from openprocurement.tender.core.procedure.models.item import (
    LocalizationItem as BaseItem,
)
from openprocurement.tender.core.procedure.models.item import (
    TechFeatureItem as TenderBaseItem,
)


class BidItem(BaseItem):
    def validate_quantity(self, data, value):
        pass


class Item(TenderBaseItem):
    def validate_unit(self, data, value):
        pass

    def validate_quantity(self, data, value):
        pass
