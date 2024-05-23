from openprocurement.api.procedure.models.unit import Unit
from openprocurement.api.procedure.types import ModelType
from openprocurement.tender.core.procedure.models.item import (
    CPVClassification as BaseCPVClassification,
)
from openprocurement.tender.core.procedure.models.item import Item as TenderBaseItem
from openprocurement.tender.core.procedure.models.item import LocalizationItem


class CPVClassification(BaseCPVClassification):
    def validate_scheme(self, data, scheme):
        pass


class BidItem(LocalizationItem):
    def validate_quantity(self, data, value):
        pass


class Item(TenderBaseItem):
    classification = ModelType(CPVClassification, required=True)
    unit = ModelType(Unit)

    def validate_relatedBuyer(self, data, related_buyer):
        pass

    def validate_unit(self, data, value):
        pass

    def validate_quantity(self, data, value):
        pass
