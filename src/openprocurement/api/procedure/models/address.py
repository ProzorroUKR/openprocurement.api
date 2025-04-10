from schematics.types import StringType
from schematics.types.compound import ModelType
from schematics.validate import ValidationError

from openprocurement.api.constants import COUNTRIES, KATOTTG, KATOTTG_SCHEME, UA_REGIONS
from openprocurement.api.procedure.models.base import Model
from openprocurement.api.procedure.models.item import Classification


class AddressClassification(Classification):
    scheme = StringType(
        required=True,
        choices=[
            KATOTTG_SCHEME,
        ],
    )

    def validate_id(self, data, value):
        if data["scheme"] == KATOTTG_SCHEME and value not in KATOTTG:
            raise ValidationError(f"{KATOTTG_SCHEME} id not found in standards")


class Address(Model):
    streetAddress = StringType()
    locality = StringType()
    region = StringType()
    postalCode = StringType()
    countryName = StringType(required=True)
    countryName_en = StringType()
    countryName_ru = StringType()
    code = ModelType(AddressClassification)

    def validate_countryName(self, address, country_name):
        if country_name not in COUNTRIES:
            raise ValidationError("field address:countryName not exist in countries catalog")

    def validate_region(self, address, region):
        if address["countryName"] == "Україна":
            if region and region not in UA_REGIONS:
                raise ValidationError("field address:region not exist in ua_regions catalog")
        elif address["code"]:
            raise ValidationError("field address:code is allowed only for countryName 'Україна'")
