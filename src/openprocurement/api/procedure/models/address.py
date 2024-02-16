from schematics.types import StringType
from schematics.validate import ValidationError

from openprocurement.api.constants import COUNTRIES, UA_REGIONS
from openprocurement.api.procedure.models.base import Model


class Address(Model):
    streetAddress = StringType()
    locality = StringType()
    region = StringType()
    postalCode = StringType()
    countryName = StringType(required=True)
    countryName_en = StringType()
    countryName_ru = StringType()


def validate_country_name(address, country_name):
    if country_name not in COUNTRIES:
        raise ValidationError("field address:countryName not exist in countries catalog")


def validate_region(address, region):
    if address["countryName"] == "Україна":
        if region and region not in UA_REGIONS:
            raise ValidationError("field address:region not exist in ua_regions catalog")
