from schematics.types import StringType
from schematics.validate import ValidationError

from openprocurement.api.procedure.utils import is_obj_const_active
from openprocurement.api.constants import VALIDATE_ADDRESS_FROM, COUNTRIES, UA_REGIONS
from openprocurement.api.models import Model


class PatchAddress(Model):
    streetAddress = StringType()
    locality = StringType()
    region = StringType()
    postalCode = StringType()
    countryName = StringType()
    countryName_en = StringType()
    countryName_ru = StringType()


class PostAddress(PatchAddress):
    countryName = StringType(required=True)


class Address(PostAddress):
    pass


def validate_country_name(obj, address, country_name):
    if is_obj_const_active(obj, VALIDATE_ADDRESS_FROM):
        if country_name not in COUNTRIES:
            raise ValidationError("field address:countryName not exist in countries catalog")

def validate_region(obj, address, region):
    if address["countryName"] == "Україна":
        if is_obj_const_active(obj, VALIDATE_ADDRESS_FROM):
            if region and region not in UA_REGIONS:
                raise ValidationError("field address:region not exist in ua_regions catalog")
