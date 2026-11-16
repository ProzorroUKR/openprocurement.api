from uuid import uuid4

from pydantic import Field, field_validator

from openprocurement.api.constants import (
    CCCE_UA,
    CCCE_UA_SCHEME,
    PQ_PROFILE_PATTERN,
    UKTZED,
    UKTZED_SCHEME,
)
from openprocurement.api.procedure.errors import ValidationError
from openprocurement.api.procedure.models.address import Address
from openprocurement.api.procedure.models.base import Model, model_field_validator
from openprocurement.api.procedure.models.item import (
    Classification,
    CPVClassification,
    validate_additional_classifications,
    validate_ccce_ua,
)
from openprocurement.api.procedure.models.period import Period
from openprocurement.api.procedure.models.unit import Unit


class AdditionalClassification(Classification):
    @model_field_validator("id")
    def validate_id(self, value):
        if self.scheme == CCCE_UA_SCHEME and value not in CCCE_UA:
            raise ValueError(f"{CCCE_UA_SCHEME} id not found in standards")
        if self.scheme == UKTZED_SCHEME and value not in UKTZED:
            raise ValueError(f"{UKTZED_SCHEME} id not found in standards")


class Item(Model):
    id: str = Field(min_length=1, default_factory=lambda: uuid4().hex)
    classification: CPVClassification
    additionalClassifications: list[AdditionalClassification] = []
    unit: Unit | None = None  # Description of the unit which the good comes in e.g. hours, kilograms
    quantity: float | None = Field(None, ge=0)  # The number of units required
    deliveryAddress: Address | None = None
    deliveryDate: Period | None = None
    description: str  # A description of the goods, services to be provided.
    description_en: str | None = None
    description_ru: str | None = None
    profile: str | None = None

    @field_validator("profile")
    @classmethod
    def validate_profile(cls, profile: str) -> str:
        if profile:
            validate_pq_profile_pattern(profile)
        return profile

    @field_validator("additionalClassifications")
    @classmethod
    def validate_additional_classifications_items(cls, classifications: list) -> list:
        validate_ccce_ua(classifications)
        return classifications

    @model_field_validator("additionalClassifications")
    def validate_additional_classifications(self, classifications):
        validate_additional_classifications(self.classification, classifications)


def validate_pq_profile_pattern(profile):
    result = PQ_PROFILE_PATTERN.findall(profile)
    if len(result) != 1:
        raise ValidationError("The profile value doesn't match id pattern")
