from openprocurement.api.procedure.models.unit import Unit
from openprocurement.tender.openeu.procedure.models.item import Item as BaseEUItem
from openprocurement.tender.openua.procedure.models.item import Item as BaseUAItem
from openprocurement.tender.core.procedure.models.item import CPVClassification as BaseCPVClassification
from openprocurement.api.procedure.types import ModelType


class CPVClassification(BaseCPVClassification):
    def validate_scheme(self, data, scheme):
        pass


class EUItem(BaseEUItem):
    unit = ModelType(Unit)
    classification = ModelType(CPVClassification, required=True)

    def validate_unit(self, data, value):
        pass

    def validate_quantity(self, data, value):
        pass

    def validate_relatedBuyer(self, data, value):
        pass


class UAItem(BaseUAItem):
    unit = ModelType(Unit)
    classification = ModelType(CPVClassification, required=True)

    def validate_unit(self, data, value):
        pass

    def validate_quantity(self, data, value):
        pass

    def validate_relatedBuyer(self, data, value):
        pass
