from schematics.types import StringType
from schematics.types.compound import ListType, ModelType
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
    addressDetails = ListType(ModelType(AddressClassification, required=True), max_size=1)

    def validate_countryName(self, address, country_name):
        if country_name not in COUNTRIES:
            raise ValidationError("field address:countryName not exist in countries catalog")

    def validate_region(self, address, region):
        if address["countryName"] == "Україна":
            if region and region not in UA_REGIONS:
                raise ValidationError("field address:region not exist in ua_regions catalog")

    def validate_addressDetails(self, address, address_details):
        if address_details is not None:
            for detail in address_details:
                if detail["scheme"] == KATOTTG_SCHEME and address["countryName"] != "Україна":
                    raise ValidationError(f"{KATOTTG_SCHEME} is allowed only for countryName 'Україна'")
