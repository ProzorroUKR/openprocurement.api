from schematics.types import BaseType, StringType
from schematics.types.compound import ListType, ModelType

from openprocurement.api.constants import MULTI_CONTRACTS_REQUIRED_FROM
from openprocurement.api.context import get_now
from openprocurement.api.procedure.context import get_tender
from openprocurement.api.utils import get_first_revision_date
from openprocurement.api.validation import ValidationError
from openprocurement.tender.core.procedure.models.item import AdditionalClassification
from openprocurement.tender.core.procedure.models.item import (
    TechFeatureItem as BaseItem,
)
from openprocurement.tender.core.procedure.models.unit import Unit


class TenderItem(BaseItem):
    additionalClassifications = ListType(ModelType(AdditionalClassification))

    unit = ModelType(Unit)
    profile = StringType(required=True)

    def validate_relatedBuyer(self, data, related_buyer):
        if not related_buyer:
            tender = get_tender() or data
            if tender.get("buyers") and tender["status"] != "draft":
                validation_date = get_first_revision_date(tender, default=get_now())
                if validation_date >= MULTI_CONTRACTS_REQUIRED_FROM:
                    raise ValidationError(BaseType.MESSAGES["required"])

    def validate_additionalClassifications(self, data, items):
        if data.get("classification"):  # classification is not required here
            return super().validate_additionalClassifications(self, data, items)

    def validate_relatedLot(self, data, value):
        if value:
            raise ValidationError("Rogue field.")
