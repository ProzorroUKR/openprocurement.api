from openprocurement.tender.core.procedure.models.item import (
    Item as BaseItem,
    CPVClassification as BaseCPVClassification,
)
from openprocurement.tender.core.procedure.models.base import ModelType
from openprocurement.tender.core.procedure.models.unit import UnitDeprecated


class CPVClassification(BaseCPVClassification):

    def validate_scheme(self, data, scheme):
        pass


class Item(BaseItem):
    classification = ModelType(CPVClassification, required=True)
    unit = ModelType(UnitDeprecated)

    def validate_relatedBuyer(self, data, related_buyer):
        pass

    def validate_unit(self, data, value):
        pass

    def validate_quantity(self, data, value):
        pass
