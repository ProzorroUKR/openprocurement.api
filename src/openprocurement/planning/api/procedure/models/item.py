from uuid import uuid4

from schematics.exceptions import ValidationError
from schematics.types import FloatType, StringType

from openprocurement.api.constants import CCCE_UA, CCCE_UA_SCHEME
from openprocurement.api.procedure.models.address import Address
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.item import (
    Classification,
    CPVClassification,
    validate_additional_classifications,
)
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.models.unit import Unit
from openprocurement.api.procedure.types import ListType, ModelType
from openprocurement.planning.api.procedure.context import get_plan
from openprocurement.tender.core.procedure.validation import validate_ccce_ua
from openprocurement.tender.pricequotation.procedure.validation import (
    validate_profile_pattern,
)


class AdditionalClassification(Classification):
    def validate_id(self, data, value):
        if data["scheme"] == CCCE_UA_SCHEME and value not in CCCE_UA:
            raise ValidationError(f"{CCCE_UA_SCHEME} id not found in standards")


class Item(Model):
    id = StringType(required=True, min_length=1, default=lambda: uuid4().hex)
    classification = ModelType(CPVClassification, required=True)
    additionalClassifications = ListType(ModelType(AdditionalClassification, required=True), default=[])
    unit = ModelType(Unit)  # Description of the unit which the good comes in e.g. hours, kilograms
    quantity = FloatType(min_value=0)  # The number of units required
    deliveryAddress = ModelType(Address)
    deliveryDate = ModelType(Period)
    description = StringType(required=True)  # A description of the goods, services to be provided.
    description_en = StringType()
    description_ru = StringType()
    profile = StringType()

    def validate_profile(self, item, profile):
        if profile:
            validate_profile_pattern(profile)

    def validate_additionalClassifications(self, item, classifications):
        validate_additional_classifications(get_plan(), item, classifications)
        if classifications is not None:
            validate_ccce_ua(classifications)
