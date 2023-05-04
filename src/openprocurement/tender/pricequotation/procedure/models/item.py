from schematics.types import StringType, BaseType
from schematics.types.compound import ModelType, ListType
from openprocurement.api.context import get_now
from openprocurement.api.constants import PQ_MULTI_PROFILE_FROM, MULTI_CONTRACTS_REQUIRED_FROM
from openprocurement.api.validation import ValidationError
from openprocurement.api.utils import get_first_revision_date
from openprocurement.tender.pricequotation.validation import validate_profile_pattern
from openprocurement.tender.core.procedure.context import get_tender
from openprocurement.tender.core.procedure.models.unit import Unit
from openprocurement.tender.core.procedure.models.item import (
    Item as BaseItem,
    AdditionalClassification,
    validate_quantity_required,
    validate_unit_required,
)


class TenderItem(BaseItem):
    additionalClassifications = ListType(ModelType(AdditionalClassification))

    unit = ModelType(Unit)
    profile = StringType()

    def validate_profile(self, data, value):
        multi_profile_released = get_first_revision_date(get_tender(), default=get_now()) > PQ_MULTI_PROFILE_FROM
        if multi_profile_released and not value:
            raise ValidationError(BaseType.MESSAGES["required"])
        if value:
            validate_profile_pattern(value)

    def validate_relatedBuyer(self, data, related_buyer):
        if not related_buyer:
            tender = get_tender() or data
            if tender.get("buyers") and tender["status"] != "draft":
                validation_date = get_first_revision_date(tender, default=get_now())
                if validation_date >= MULTI_CONTRACTS_REQUIRED_FROM:
                    raise ValidationError(BaseType.MESSAGES["required"])

    def validate_unit(self, data, value):
        return validate_unit_required(data, value)

    def validate_quantity(self, data, value):
        return validate_quantity_required(data, value)

    def validate_additionalClassifications(self, data, items):
        if data.get("classification"):  # classification is not required here
            return super().validate_additionalClassifications(self, data, items)

    def validate_relatedLot(self, data, value):
        if value:
            raise ValidationError("Rogue field.")
