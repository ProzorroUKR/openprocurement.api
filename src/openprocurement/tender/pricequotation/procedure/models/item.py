from schematics.types.compound import ListType, ModelType

from openprocurement.api.procedure.models.unit import Unit
from openprocurement.api.validation import ValidationError
from openprocurement.tender.core.procedure.models.item import AdditionalClassification
from openprocurement.tender.core.procedure.models.item import (
    TechFeatureItem as BaseItem,
)


class TenderItem(BaseItem):
    additionalClassifications = ListType(ModelType(AdditionalClassification, required=True))
    unit = ModelType(Unit)

    def validate_additionalClassifications(self, data, items):
        if data.get("classification"):  # classification is not required here
            return super().validate_additionalClassifications(self, data, items)

    def validate_relatedLot(self, data, value):
        if value:
            raise ValidationError("Rogue field.")
