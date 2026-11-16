from enum import StrEnum
from typing import Any, ClassVar
from uuid import uuid4

from pydantic import Field, model_validator

from openprocurement.api.constants import (
    ADDITIONAL_CLASSIFICATIONS_SCHEMES,
    CCCE_UA,
    CCCE_UA_SCHEME,
    CPV_CODES,
    CPV_NOT_CPV,
    DK_CODES,
    GMDN_2019,
    GMDN_2019_SCHEME,
    GMDN_2023,
    GMDN_2023_SCHEME,
    KEKV_UK,
    KEKV_UK_SCHEME,
    KPKV_UK,
    KPKV_UK_SCHEME,
    UA_ROAD,
    UA_ROAD_SCHEME,
)
from openprocurement.api.procedure.errors import FieldError, FieldErrors, ValidationError
from openprocurement.api.procedure.models.base import Model, model_field_validator
from openprocurement.api.procedure.types import Url


class CPVScheme(StrEnum):
    CPV = "CPV"
    DK021 = "ДК021"


ADDITIONAL_CLASSIFICATIONS: dict[str, dict] = {
    UA_ROAD_SCHEME: UA_ROAD,
    GMDN_2019_SCHEME: GMDN_2019,
    GMDN_2023_SCHEME: GMDN_2023,
    CCCE_UA_SCHEME: CCCE_UA,
    KPKV_UK_SCHEME: KPKV_UK,
    KEKV_UK_SCHEME: KEKV_UK,
}


class Classification(Model):
    scheme: str  # The classification scheme for the goods
    id: str  # The classification ID from the Scheme used
    description: str  # A description of the goods, services to be provided.
    description_en: str | None = None
    description_ru: str | None = None
    uri: Url | None = None


class CPVClassification(Classification):
    # only ДК021 is allowed, the CPV scheme stays in the choices for the old objects
    dk021_scheme_required: ClassVar[bool] = True

    scheme: CPVScheme = CPVScheme.CPV
    id: str

    @model_validator(mode="after")
    def validate_cpv(self):
        errors = {}
        if self.scheme == CPVScheme.CPV and self.id not in CPV_CODES:
            errors["id"] = "Value must be one of CPV codes"
        elif self.scheme == CPVScheme.DK021 and self.id not in DK_CODES:
            errors["id"] = f"Value must be one of {CPVScheme.DK021} codes"
        if self.dk021_scheme_required and self.scheme != CPVScheme.DK021:  # the default one is not allowed as well
            errors["scheme"] = f"Value must be one of {[CPVScheme.DK021.value]}."
        if errors:
            raise FieldErrors(errors)
        return self


class AdditionalClassification(Classification):
    @model_field_validator("id")
    def validate_id(self, value):
        if self.scheme in ADDITIONAL_CLASSIFICATIONS and value not in ADDITIONAL_CLASSIFICATIONS[self.scheme]:
            raise ValueError(f"{self.scheme} id not found in standards")

    @model_field_validator("description")
    def validate_description(self, value):
        if self.scheme == UA_ROAD_SCHEME and UA_ROAD.get(self.id) != value:
            raise ValueError(f"{UA_ROAD_SCHEME} description invalid")


def validate_additional_classifications(classification: Any, items: list | None) -> None:
    """`classification` is the main (CPV) classification of the object the additional classifications belong to"""
    if (
        classification
        and classification.id == CPV_NOT_CPV
        and items
        and not any(i.scheme in ADDITIONAL_CLASSIFICATIONS_SCHEMES for i in items)
    ):
        raise ValueError(
            "One of additional classifications should be one of [{}].".format(
                ", ".join(ADDITIONAL_CLASSIFICATIONS_SCHEMES)
            )
        )


class Location(Model):
    latitude: Any
    longitude: Any
    elevation: Any = None


class Item(Model):
    """A good, service, or work to be contracted."""

    id: str = Field(min_length=1, default_factory=lambda: uuid4().hex)
    description: str  # A description of the goods, services to be provided.
    description_en: str | None = None
    description_ru: str | None = None
    classification: CPVClassification | None = None
    additionalClassifications: list[AdditionalClassification] = []
    quantity: float | None = Field(None, ge=0)  # The number of units required
    deliveryLocation: Location | None = None


class TechFeatureItemMixin(Model):
    profile: str | None = None
    category: str | None = None

    @model_validator(mode="after")
    def validate_profile(self):
        if self.profile and not self.category:
            raise FieldError("profile", "profile should be provided together only with category")
        return self


def validate_ccce_ua(additional_classifications):
    ccce_count = sum(1 for i in additional_classifications if i.scheme == CCCE_UA_SCHEME)
    if ccce_count > 1:
        raise ValidationError(
            f"Object shouldn't have more than 1 additionalClassification with scheme {CCCE_UA_SCHEME}"
        )
