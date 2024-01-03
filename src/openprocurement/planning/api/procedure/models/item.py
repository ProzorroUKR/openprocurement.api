from uuid import uuid4

from schematics.types import StringType, FloatType

from openprocurement.api.models import Model
from openprocurement.api.procedure.models.base import ModelType, ListType
from openprocurement.api.procedure.models.item import (
    Classification,
    validate_additional_classifications,
    validate_scheme,
)
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.models.item import (
    CPVClassification as BaseCPVClassification,
)
from openprocurement.tender.pricequotation.procedure.validation import validate_profile_pattern
from openprocurement.planning.api.procedure.context import get_plan
from openprocurement.planning.api.procedure.models.address import Address
from openprocurement.planning.api.procedure.models.unit import Unit


class CPVClassification(BaseCPVClassification):
    def validate_scheme(self, classification, scheme):
        validate_scheme(get_plan(), scheme)


class Item(Model):
    id = StringType(required=True, min_length=1, default=lambda: uuid4().hex)
    classification = ModelType(CPVClassification, required=True)
    additionalClassifications = ListType(ModelType(Classification, required=True), default=list())
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
