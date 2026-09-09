from openprocurement.api.procedure.models.item import CPVClassification
from openprocurement.api.procedure.types import ModelType
from openprocurement.tender.core.procedure.models.item import Item


class CDCPVClassification(CPVClassification):
    def validate_scheme(self, data, scheme):
        pass


class CDItem(Item):
    classification = ModelType(CDCPVClassification, required=True)
