from enum import StrEnum

from pydantic import Field, field_validator

from openprocurement.api.constants import COUNTRIES, KATOTTG, KATOTTG_SCHEME, UA_REGIONS
from openprocurement.api.procedure.models.base import Model, model_field_validator
from openprocurement.api.procedure.models.item import Classification


class CountryName(StrEnum):
    UKRAINE = "Україна"


class AddressClassificationScheme(StrEnum):
    KATOTTG = KATOTTG_SCHEME


class AddressClassification(Classification):
    scheme: AddressClassificationScheme

    @model_field_validator("id")
    def validate_id(self, value):
        if self.scheme == KATOTTG_SCHEME and value not in KATOTTG:
            raise ValueError(f"{KATOTTG_SCHEME} id not found in standards")


def validate_country_name(country_name: str) -> None:
    if country_name not in COUNTRIES:
        raise ValueError("field address:countryName not exist in countries catalog")


def validate_region(country_name: str | None, region: str | None) -> None:
    if country_name == CountryName.UKRAINE and region and region not in UA_REGIONS:
        raise ValueError("field address:region not exist in ua_regions catalog")


class Address(Model):
    streetAddress: str | None = None
    locality: str | None = None
    region: str | None = None
    postalCode: str | None = None
    countryName: str
    countryName_en: str | None = None
    countryName_ru: str | None = None
    addressDetails: list[AddressClassification] | None = Field(None, max_length=1)

    @field_validator("countryName")
    @classmethod
    def validate_country_name(cls, country_name: str) -> str:
        validate_country_name(country_name)
        return country_name

    @model_field_validator("addressDetails")
    def validate_address_details(self, address_details):
        if self.countryName and self.countryName != CountryName.UKRAINE:
            if any(detail.scheme == KATOTTG_SCHEME for detail in address_details or []):
                raise ValueError(f"{KATOTTG_SCHEME} is allowed only for countryName '{CountryName.UKRAINE}'")

    @model_field_validator("region")
    def validate_region(self, region):
        validate_region(self.countryName, region)
